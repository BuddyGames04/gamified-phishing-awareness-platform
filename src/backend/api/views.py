from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Email, InteractionEvent, UserProgress, Scenario
from .serializers import (
    EmailSerializer,
    InteractionEventSerializer,
    UserProgressSerializer,
    ScenarioSerializer,
)


@api_view(["GET"])
def get_emails(request):
    mode = request.query_params.get("mode")  # "arcade" or "simulation"
    scenario_id = request.query_params.get("scenario_id")

    emails = Email.objects.all()

    if mode:
        emails = emails.filter(mode=mode)

    if scenario_id:
        emails = emails.filter(scenario_id=scenario_id)

    emails = emails.order_by("id")
    
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
