# src/backend/api/views_leaderboard.py
from __future__ import annotations

from django.db.models import Avg, Case, Count, IntegerField, Sum, Value, When
from django.db.models.functions import Coalesce
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import ArcadeAttempt, LevelRun


def _safe_int(x, default: int) -> int:
    try:
        return int(x)
    except Exception:
        return default


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_leaderboard(request):
    """
    GET /api/leaderboard/?mode=overall|arcade|simulation|pvp&sort=desc|asc&q=...&limit=50
    Returns rows:
      { user_id, score, runs, correct, incorrect, avg_duration_ms }
    """
    mode = (request.query_params.get("mode") or "overall").lower().strip()
    sort = (request.query_params.get("sort") or "desc").lower().strip()
    q = (request.query_params.get("q") or "").strip()
    limit = _safe_int(request.query_params.get("limit"), 50)
    limit = max(1, min(limit, 200))

    # -------------------------
    # A) Simulation + PVP totals (from LevelRun.points)
    # -------------------------
    run_qs = LevelRun.objects.filter(completed_at__isnull=False)

    if mode in ("simulation", "pvp"):
        run_qs = run_qs.filter(mode=mode)

    if q:
        run_qs = run_qs.filter(user_id__icontains=q)

    run_rows = list(
        run_qs.values("user_id")
        .annotate(
            score=Coalesce(Sum("points"), 0),
            runs=Count("id"),
            correct=Coalesce(Sum("correct"), 0),
            incorrect=Coalesce(Sum("incorrect"), 0),
            avg_duration_ms=Avg("client_duration_ms"),
        )
    )

    runs_by_user = {r["user_id"]: r for r in run_rows}

    # -------------------------
    # B) Arcade totals (computed on-the-fly from ArcadeAttempt)
    # points per attempt:
    #   +60 correct
    #   -20 wrong
    # (keep time factor optional for now — client can do fancy later)
    # -------------------------
    arcade_rows = []
    if mode in ("overall", "arcade"):
        arcade_qs = ArcadeAttempt.objects.all()
        if q:
            arcade_qs = arcade_qs.filter(user_id__icontains=q)

        arcade_rows = list(
            arcade_qs.values("user_id")
            .annotate(
                score=Coalesce(
                    Sum(
                        Case(
                            When(was_correct=True, then=Value(60)),
                            default=Value(-20),
                            output_field=IntegerField(),
                        )
                    ),
                    0,
                ),
                runs=Count("id"),
                correct=Coalesce(
                    Sum(
                        Case(
                            When(was_correct=True, then=Value(1)),
                            default=Value(0),
                            output_field=IntegerField(),
                        )
                    ),
                    0,
                ),
                incorrect=Coalesce(
                    Sum(
                        Case(
                            When(was_correct=False, then=Value(1)),
                            default=Value(0),
                            output_field=IntegerField(),
                        )
                    ),
                    0,
                ),
                avg_duration_ms=Avg("response_time_ms"),
            )
        )

    arcade_by_user = {r["user_id"]: r for r in arcade_rows}

    # -------------------------
    # Combine by requested mode
    # -------------------------
    rows = []

    if mode == "simulation" or mode == "pvp":
        # only LevelRun aggregation
        for user_id, r in runs_by_user.items():
            rows.append(
                {
                    "user_id": user_id,
                    "score": int(r["score"] or 0),
                    "runs": int(r["runs"] or 0),
                    "correct": int(r["correct"] or 0),
                    "incorrect": int(r["incorrect"] or 0),
                    "avg_duration_ms": r["avg_duration_ms"],
                }
            )

    elif mode == "arcade":
        # only arcade aggregation
        for user_id, r in arcade_by_user.items():
            rows.append(
                {
                    "user_id": user_id,
                    "score": int(r["score"] or 0),
                    "runs": int(r["runs"] or 0),
                    "correct": int(r["correct"] or 0),
                    "incorrect": int(r["incorrect"] or 0),
                    "avg_duration_ms": r["avg_duration_ms"],
                }
            )

    else:
        # overall = runs + arcade merged
        user_ids = set(runs_by_user.keys()) | set(arcade_by_user.keys())
        for user_id in user_ids:
            r = runs_by_user.get(user_id)
            a = arcade_by_user.get(user_id)

            score = int((r["score"] if r else 0) or 0) + int((a["score"] if a else 0) or 0)
            runs = int((r["runs"] if r else 0) or 0) + int((a["runs"] if a else 0) or 0)
            correct = int((r["correct"] if r else 0) or 0) + int((a["correct"] if a else 0) or 0)
            incorrect = int((r["incorrect"] if r else 0) or 0) + int((a["incorrect"] if a else 0) or 0)

            # avg duration: keep it simple; prefer run duration if present else arcade
            avg_dur = (r["avg_duration_ms"] if r and r["avg_duration_ms"] is not None else None)
            if avg_dur is None:
                avg_dur = (a["avg_duration_ms"] if a and a["avg_duration_ms"] is not None else None)

            rows.append(
                {
                    "user_id": user_id,
                    "score": score,
                    "runs": runs,
                    "correct": correct,
                    "incorrect": incorrect,
                    "avg_duration_ms": avg_dur,
                }
            )

    # sort (server-side baseline; you can still do “algorithm showcase” client-side)
    reverse = sort != "asc"
    rows.sort(key=lambda x: (x["score"], x["runs"], x["user_id"]), reverse=reverse)

    return Response({"mode": mode, "count": len(rows), "rows": rows[:limit]})