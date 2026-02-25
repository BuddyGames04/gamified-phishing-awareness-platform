# src/backend/api/views.py
import random

from django.db.models import F
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Email, InteractionEvent, Level, LevelEmail, Scenario, UserProgress
from .serializers import (
    EmailSerializer,
    InteractionEventSerializer,
    ScenarioSerializer,
    UserProgressSerializer,
)


@api_view(["GET"])
def get_emails(request):
    mode = request.query_params.get("mode")  # arcade|simulation
    limit = int(request.query_params.get("limit", "20"))

    if mode == "simulation":
        scenario_id = request.query_params.get("scenario_id")
        level = request.query_params.get("level")
        if not level:
            return Response({"detail": "level required"}, status=400)

        try:
            level_num = int(level)
        except ValueError:
            return Response({"detail": "level must be an integer"}, status=400)

        lvl = None
        if scenario_id:
            try:
                lvl = Level.objects.get(scenario_id=scenario_id, number=level_num)
            except Level.DoesNotExist:
                lvl = None

        if lvl is None:
            try:
                lvl = Level.objects.get(number=level_num)
            except Level.DoesNotExist:
                return Response({"detail": "Level not found"}, status=404)

        wave_true = str(request.query_params.get("wave", "")).lower() in (
            "1",
            "true",
            "yes",
            "y",
            "on",
        )
        sort_filter = (
            {"in_levels__sort_order__gte": 100}
            if wave_true
            else {"in_levels__sort_order__lt": 100}
        )

        emails = (
            Email.objects.filter(in_levels__level=lvl, **sort_filter)
            .annotate(
                current_level_number=F("in_levels__level__number"),
                level_sort_order=F("in_levels__sort_order"),
            )
            .order_by("level_sort_order", "id")[:limit]
        )
        return Response(EmailSerializer(emails, many=True).data)

    # arcade fallback: just return random arcade emails (until /arcade/next is ready)
    emails = Email.objects.filter(mode="arcade").order_by("?")[:limit]
    return Response(EmailSerializer(emails, many=True).data)


@api_view(["GET"])
def get_scenarios(request):
    scenarios = Scenario.objects.all()
    serializer = ScenarioSerializer(scenarios, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_result(request):
    user_id = request.user.username
    is_correct = request.data.get("is_correct")

    progress, _ = UserProgress.objects.get_or_create(user_id=user_id)
    progress.total_attempts += 1
    if is_correct:
        progress.correct += 1
        progress.score += 10
    else:
        progress.incorrect += 1
        progress.score = max(progress.score - 2, 0)
    progress.save()

    serializer = UserProgressSerializer(progress)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def record_interaction(request):
    user_id = request.user.username
    email_id = request.data.get("email_id")
    event_type = request.data.get("event_type")
    value = request.data.get("value", None)

    if not email_id or not event_type:
        return Response(
            {"detail": "email_id and event_type are required"},
            status=400,
        )

    try:
        email = Email.objects.get(id=email_id)
    except Email.DoesNotExist:
        return Response({"detail": "Email not found"}, status=404)

    event = InteractionEvent.objects.create(
        user_id=user_id,
        email=email,
        event_type=event_type,
        value=value,
    )

    serializer = InteractionEventSerializer(event)
    return Response(serializer.data, status=201)
