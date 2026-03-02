# src/backend/api/views_metrics.py
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    ArcadeAttempt,
    ArcadeState,
    Email,
    EmailDecisionEvent,
    InteractionEvent,
    Level,
    LevelRun,
    Scenario,
)
from .models_pvp import PvpLevel  # needed for creator metrics
from .serializers_metrics import (
    CompleteRunSerializer,
    DecisionCreateSerializer,
    StartRunResponseSerializer,
    StartRunSerializer,
)


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _mode_weight(mode: str) -> float:
    if mode == "arcade":
        return 0.6
    if mode == "simulation":
        return 1.0
    if mode == "pvp":
        return 1.1
    return 1.0


def _sim_level_weight(level_number: int) -> float:
    # bands: 1–3, 4–6, 7–10, 11–15, 16–20
    if level_number <= 3:
        return 0.9
    if level_number <= 6:
        return 1.0
    if level_number <= 10:
        return 1.1
    if level_number <= 15:
        return 1.2
    return 1.3


def _base_points(correct: int, incorrect: int) -> int:
    total = max(0, (correct or 0) + (incorrect or 0))
    if total == 0:
        return 0
    acc = (correct or 0) / total
    return int(round(1000 * acc))


def _weighted_points(mode: str, level_number: int, correct: int, incorrect: int) -> int:
    base = _base_points(correct, incorrect)
    mw = _mode_weight(mode)
    lw = _sim_level_weight(level_number) if mode == "simulation" else 1.0
    return int(round(base * mw * lw))


class StartLevelRunView(APIView):
    """
    POST /api/metrics/level-runs/start/
    Body: { user_id, mode, scenario_id?, level_number, emails_total }
    """

    def post(self, request):
        ser = StartRunSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        user_id = data["user_id"]
        mode = data["mode"]
        scenario_id = data.get("scenario_id")
        level_number = data["level_number"]
        emails_total = data["emails_total"]

        scenario = None
        level = None

        if scenario_id is not None:
            scenario = Scenario.objects.filter(id=scenario_id).first()
            if scenario:
                level = Level.objects.filter(
                    scenario=scenario, number=level_number
                ).first()

        run = LevelRun.objects.create(
            user_id=user_id,
            mode=mode,
            scenario=scenario,
            level=level,
            level_number=level_number,
            emails_total=emails_total,
        )

        return Response(
            StartRunResponseSerializer(run).data, status=status.HTTP_201_CREATED
        )


class CompleteLevelRunView(APIView):
    """
    POST /api/metrics/level-runs/<run_id>/complete/
    Body: { correct, incorrect }
    """

    def post(self, request, run_id: int):
        run = get_object_or_404(LevelRun, id=run_id)
        ser = CompleteRunSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        run.mark_complete(
            correct=ser.validated_data["correct"],
            incorrect=ser.validated_data["incorrect"],
        )
        return Response({"ok": True, "run_id": run.id})


class CreateDecisionEventView(APIView):
    """
    POST /api/metrics/decisions/
    Body: { user_id, run_id?, email_id, decision, was_correct }

    Server computes:
      had_link_click / had_attachment_open from InteractionEvent between run.started_at and decision time.
    """

    def post(self, request):
        ser = DecisionCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        user_id = data["user_id"]
        run_id = data.get("run_id")
        email = get_object_or_404(Email, id=data["email_id"])

        run = None
        run_started_at = None
        if run_id:
            run = LevelRun.objects.filter(id=run_id).first()
            if run:
                run_started_at = run.started_at

        # Compute risk flags from InteractionEvent
        # If we can't find a run, fall back to "any time" for that user+email.
        qs = InteractionEvent.objects.filter(user_id=user_id, email=email)

        if run_started_at:
            qs = qs.filter(created_at__gte=run_started_at)

        had_link = qs.filter(event_type="link_click").exists()
        had_attach = qs.filter(event_type="attachment_open").exists()

        decision_event = EmailDecisionEvent.objects.create(
            user_id=user_id,
            run=run,
            email=email,
            decision=data["decision"],
            was_correct=data["was_correct"],
            had_link_click=had_link,
            had_attachment_open=had_attach,
        )

        return Response(
            {
                "id": decision_event.id,
                "had_link_click": decision_event.had_link_click,
                "had_attachment_open": decision_event.had_attachment_open,
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileMetricsView(APIView):
    """
    GET /api/profile/metrics/?user_id=Luke

    Returns:
      - overall stats
      - recent runs
      - by_level aggregates
      - trends arrays (simple)
    """

    def get(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response(
                {"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        runs = LevelRun.objects.filter(
            user_id=user_id, completed_at__isnull=False
        ).order_by("-completed_at")
        decisions = EmailDecisionEvent.objects.filter(user_id=user_id).order_by(
            "-created_at"
        )

        # Overall
        total_runs = runs.count()
        total_correct = runs.aggregate(x=Sum("correct"))["x"] or 0
        total_incorrect = runs.aggregate(x=Sum("incorrect"))["x"] or 0
        total_attempts = total_correct + total_incorrect
        accuracy = (total_correct / total_attempts) if total_attempts > 0 else 0.0

        total_decisions = decisions.count()
        link_before = decisions.filter(had_link_click=True).count()
        attach_before = decisions.filter(had_attachment_open=True).count()

        pct_link_before = (
            (link_before / total_decisions) if total_decisions > 0 else 0.0
        )
        pct_attach_before = (
            (attach_before / total_decisions) if total_decisions > 0 else 0.0
        )

        # Recent runs (last 10)
        recent_runs = []
        for r in runs[:10]:
            attempts = r.correct + r.incorrect
            recent_runs.append(
                {
                    "run_id": r.id,
                    "mode": r.mode,  # keep consistent with frontend table
                    "level_number": r.level_number,
                    "scenario_id": r.scenario_id,
                    "emails_total": r.emails_total,
                    "correct": r.correct,
                    "incorrect": r.incorrect,
                    "attempts": attempts,
                    "accuracy": (r.correct / attempts) if attempts > 0 else 0.0,
                    "started_at": r.started_at,
                    "completed_at": r.completed_at,
                }
            )

        # Aggregate by level_number
        by_level_qs = (
            runs.values("level_number")
            .annotate(
                runs=Count("id"),
                correct=Sum("correct"),
                incorrect=Sum("incorrect"),
            )
            .order_by("level_number")
        )

        by_level = []
        for row in by_level_qs:
            attempts = (row["correct"] or 0) + (row["incorrect"] or 0)
            by_level.append(
                {
                    "level_number": row["level_number"],
                    "scenario_id": None,  # keep the field present for your table key
                    "runs": row["runs"],
                    "correct": row["correct"] or 0,
                    "incorrect": row["incorrect"] or 0,
                    "accuracy": (
                        ((row["correct"] or 0) / attempts) if attempts > 0 else 0.0
                    ),
                    "attempts": attempts,
                    "last_played_at": None,
                }
            )

        # Trend shape matches TS: { date: string, accuracy: number, ... }
        trend_accuracy = []
        for r in reversed(list(runs[:20])):
            attempts = (r.correct or 0) + (r.incorrect or 0)
            trend_accuracy.append(
                {
                    "date": r.completed_at.isoformat() if r.completed_at else None,
                    "accuracy": ((r.correct or 0) / attempts) if attempts > 0 else 0.0,
                }
            )

        # ----------------------------
        # Arcade metrics (flat attempts)
        # ----------------------------
        arcade_attempts_qs = ArcadeAttempt.objects.filter(user_id=user_id).order_by(
            "id"
        )
        arcade_total = arcade_attempts_qs.count()
        arcade_correct = arcade_attempts_qs.filter(was_correct=True).count()
        arcade_incorrect = arcade_total - arcade_correct
        arcade_accuracy = (arcade_correct / arcade_total) if arcade_total > 0 else 0.0

        # Response time (ignore nulls)
        rt_vals = list(
            arcade_attempts_qs.exclude(response_time_ms__isnull=True).values_list(
                "response_time_ms", flat=True
            )
        )
        arcade_avg_rt = (sum(rt_vals) / len(rt_vals)) if rt_vals else None

        # Difficulty faced (from stored email_difficulty)
        diffs = list(arcade_attempts_qs.values_list("email_difficulty", flat=True))
        diffs = [d for d in diffs if d is not None]
        arcade_avg_email_diff = (sum(diffs) / len(diffs)) if diffs else None

        # Current target difficulty (from ArcadeState if available, else last attempt target)
        arcade_state = ArcadeState.objects.filter(user_id=user_id).first()
        arcade_target_now = (
            float(arcade_state.difficulty_float) if arcade_state is not None else None
        )
        if arcade_target_now is None:
            last_target = arcade_attempts_qs.values_list(
                "target_difficulty", flat=True
            ).last()
            arcade_target_now = float(last_target) if last_target is not None else None

        # Streak + longest streak computed from attempt history
        cur_streak = 0
        best_streak = 0
        for was_correct in arcade_attempts_qs.values_list("was_correct", flat=True):
            if was_correct:
                cur_streak += 1
                if cur_streak > best_streak:
                    best_streak = cur_streak
            else:
                cur_streak = 0

        # Accuracy by difficulty bucket (1-2 / 3 / 4-5)
        def bucket(d: int) -> str:
            if d is None:
                return "unknown"
            if d <= 2:
                return "1-2"
            if d == 3:
                return "3"
            return "4-5"

        by_bucket = {
            "1-2": {"n": 0, "c": 0},
            "3": {"n": 0, "c": 0},
            "4-5": {"n": 0, "c": 0},
        }
        for d, wc in arcade_attempts_qs.values_list("email_difficulty", "was_correct"):
            b = bucket(d)
            if b in by_bucket:
                by_bucket[b]["n"] += 1
                if wc:
                    by_bucket[b]["c"] += 1

        arcade_accuracy_by_bucket = []
        for b in ["1-2", "3", "4-5"]:
            n = by_bucket[b]["n"]
            c = by_bucket[b]["c"]
            arcade_accuracy_by_bucket.append(
                {
                    "bucket": b,
                    "attempts": n,
                    "accuracy": (c / n) if n > 0 else 0.0,
                }
            )

        # ----------------
        # Overall (ALL MODES) + PVP metrics
        # ----------------
        sim_runs = LevelRun.objects.filter(
            user_id=user_id, mode="simulation", completed_at__isnull=False
        )
        arcade_attempts = ArcadeAttempt.objects.filter(user_id=user_id)

        sim_correct = sim_runs.aggregate(x=Sum("correct"))["x"] or 0
        sim_incorrect = sim_runs.aggregate(x=Sum("incorrect"))["x"] or 0

        arcade_total_all = arcade_attempts.count()
        arcade_correct_all = arcade_attempts.filter(was_correct=True).count()
        arcade_incorrect_all = arcade_total_all - arcade_correct_all

        # ----------------------------
        # PVP metrics
        # ----------------------------
        # A) Playing metrics (your decisions on shadow emails mode="pvp")
        pvp_decisions_playing = EmailDecisionEvent.objects.filter(
            user_id=user_id,
            email__mode="pvp",
        )

        pvp_total = pvp_decisions_playing.count()
        pvp_correct = pvp_decisions_playing.filter(was_correct=True).count()
        pvp_incorrect = pvp_total - pvp_correct
        pvp_accuracy = (pvp_correct / pvp_total) if pvp_total > 0 else 0.0

        pvp_link_before = pvp_decisions_playing.filter(had_link_click=True).count()
        pvp_attach_before = pvp_decisions_playing.filter(
            had_attachment_open=True
        ).count()
        pvp_pct_link_before = (pvp_link_before / pvp_total) if pvp_total > 0 else 0.0
        pvp_pct_attach_before = (
            (pvp_attach_before / pvp_total) if pvp_total > 0 else 0.0
        )

        # B) Creator metrics (other people’s decisions on your posted/owned levels)
        # NOTE: This relies on Email.pvp_level FK being set on the shadow Email.
        pvp_decisions_on_my_levels = EmailDecisionEvent.objects.filter(
            email__mode="pvp",
            email__pvp_level__owner__username=user_id,
        )

        creator_total = pvp_decisions_on_my_levels.count()
        creator_correct = pvp_decisions_on_my_levels.filter(was_correct=True).count()
        creator_incorrect = creator_total - creator_correct
        creator_accuracy = (
            (creator_correct / creator_total) if creator_total > 0 else 0.0
        )

        creator_unique_players = (
            pvp_decisions_on_my_levels.values("user_id").distinct().count()
            if creator_total > 0
            else 0
        )

        creator_levels_posted = PvpLevel.objects.filter(
            owner__username=user_id, visibility="posted"
        ).count()
        creator_levels_total = PvpLevel.objects.filter(owner__username=user_id).count()

        overall_all_attempts = (
            (sim_correct + sim_incorrect) + arcade_total_all + pvp_total
        )
        overall_all_correct = sim_correct + arcade_correct_all + pvp_correct
        overall_all_incorrect = sim_incorrect + arcade_incorrect_all + pvp_incorrect

        overall_all_accuracy = (
            (overall_all_correct / overall_all_attempts)
            if overall_all_attempts > 0
            else 0.0
        )

        return Response(
            {
                "user_id": user_id,
                "overall": {
                    "total_runs": total_runs,
                    "total_attempts": total_attempts,
                    "accuracy": accuracy,
                    "decision_events": total_decisions,
                    "pct_link_click_before_decision": pct_link_before,
                    "pct_attachment_open_before_decision": pct_attach_before,
                },
                "overall_all": {
                    "total_attempts": overall_all_attempts,
                    "correct": overall_all_correct,
                    "incorrect": overall_all_incorrect,
                    "accuracy": overall_all_accuracy,
                    "arcade_attempts": arcade_total_all,
                    "inbox_attempts": (sim_correct + sim_incorrect),
                    "pvp_attempts": pvp_total,
                },
                "recent_runs": recent_runs,
                "by_level": by_level,
                "trends": {"accuracy": trend_accuracy},
                "arcade": {
                    "total_attempts": arcade_total,
                    "correct": arcade_correct,
                    "incorrect": arcade_incorrect,
                    "accuracy": arcade_accuracy,
                    "avg_response_time_ms": arcade_avg_rt,
                    "avg_email_difficulty": arcade_avg_email_diff,
                    "target_difficulty_now": arcade_target_now,
                    "current_streak": cur_streak,
                    "best_streak": best_streak,
                    "accuracy_by_difficulty_bucket": arcade_accuracy_by_bucket,
                },
                "pvp": {
                    "playing": {
                        "total_attempts": pvp_total,
                        "correct": pvp_correct,
                        "incorrect": pvp_incorrect,
                        "accuracy": pvp_accuracy,
                        "pct_link_before": pvp_pct_link_before,
                        "pct_attach_before": pvp_pct_attach_before,
                    },
                    "creator": {
                        "levels_total": creator_levels_total,
                        "levels_posted": creator_levels_posted,
                        "total_attempts": creator_total,
                        "correct": creator_correct,
                        "incorrect": creator_incorrect,
                        "accuracy": creator_accuracy,
                        "unique_players": creator_unique_players,
                    },
                },
            }
        )
