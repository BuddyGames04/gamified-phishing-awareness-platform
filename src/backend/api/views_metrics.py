from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Email,
    EmailDecisionEvent,
    InteractionEvent,
    Level,
    LevelRun,
    Scenario,
)
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
            user_id=user_id, mode="simulation", completed_at__isnull=False
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
                    "level_number": r.level_number,
                    "scenario_id": r.scenario_id,
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
                    "runs": row["runs"],
                    "accuracy": (
                        ((row["correct"] or 0) / attempts) if attempts > 0 else 0.0
                    ),
                    "attempts": attempts,
                }
            )

        trend_accuracy = []
        for r in reversed(list(runs[:20])):
            attempts = r.correct + r.incorrect
            trend_accuracy.append(
                {
                    "t": r.completed_at,
                    "accuracy": (r.correct / attempts) if attempts > 0 else 0.0,
                    "level_number": r.level_number,
                }
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
                "recent_runs": recent_runs,
                "by_level": by_level,
                "trends": {
                    "accuracy": trend_accuracy,
                },
            }
        )
