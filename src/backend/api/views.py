from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Email, InteractionEvent, Scenario, UserProgress, Level, LevelEmail
from .serializers import (
    EmailSerializer,
    InteractionEventSerializer,
    ScenarioSerializer,
    UserProgressSerializer,
)

import random


@api_view(["GET"])
def get_emails(request):
    mode = request.query_params.get("mode")  # arcade|simulation
    scenario_id = request.query_params.get("scenario_id")
    min_d = request.query_params.get("min_difficulty")
    max_d = request.query_params.get("max_difficulty")
    limit = int(request.query_params.get("limit", "20"))
    level = request.query_params.get("level")


    if mode == "simulation" and scenario_id and level:
        try:
            lvl = Level.objects.get(scenario_id=scenario_id, number=int(level))
        except Level.DoesNotExist:
            return Response({"detail": "Level not found"}, status=404)

        emails = Email.objects.filter(in_levels__level=lvl).order_by("in_levels__sort_order", "id")
        serializer = EmailSerializer(emails, many=True)
        return Response(serializer.data)
    emails = Email.objects.all()

    if mode:
        emails = emails.filter(mode=mode)

    if scenario_id:
        emails = emails.filter(scenario_id=scenario_id)

    if min_d:
        emails = emails.filter(difficulty__gte=int(min_d))
    if max_d:
        emails = emails.filter(difficulty__lte=int(max_d))

    if level:
        emails = emails.filter(level_number__lte=int(level) + 2)

    emails = list(emails.order_by("id"))
    random.shuffle(emails)
    emails = emails[:limit]

    serializer = EmailSerializer(emails, many=True)
    return Response(serializer.data)

@api_view(["GET"])
def get_scenarios(request):
    scenarios = Scenario.objects.all()
    serializer = ScenarioSerializer(scenarios, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def submit_result(request):
    user_id = request.data.get("user_id")
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
def record_interaction(request):
    user_id = request.data.get("user_id")
    email_id = request.data.get("email_id")
    event_type = request.data.get("event_type")
    value = request.data.get("value", None)

    if not user_id or not email_id or not event_type:
        return Response(
            {"detail": "user_id, email_id, and event_type are required"},
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
