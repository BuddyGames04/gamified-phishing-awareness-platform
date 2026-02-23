import random
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Email, ArcadeAttempt, ArcadeState
from .serializers import EmailSerializer


RECENT_WINDOW = 25          # don’t repeat last N
TARGET_MIN = 1.0
TARGET_MAX = 5.0            # your Email.difficulty is 1..5

def _pick_email(user_id: str, target_d: int):
    # exclude recently seen
    recent_ids = list(
        ArcadeAttempt.objects.filter(user_id=user_id)
        .values_list("email_id", flat=True)[:RECENT_WINDOW]
    )

    # Prefer exact difficulty, then +/-1 if needed
    candidates = Email.objects.filter(mode="arcade").exclude(id__in=recent_ids)

    exact = candidates.filter(difficulty=target_d)
    if exact.exists():
        return exact.order_by("?").first()

    band = candidates.filter(difficulty__in=[max(1, target_d - 1), min(5, target_d + 1)])
    if band.exists():
        return band.order_by("?").first()

    # fallback: allow repeats if pool is small
    fallback = Email.objects.filter(mode="arcade", difficulty=target_d)
    if fallback.exists():
        return fallback.order_by("?").first()

    return Email.objects.filter(mode="arcade").order_by("?").first()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_arcade_next(request):
    user_id = request.user.username
    state, _ = ArcadeState.objects.get_or_create(user_id=user_id)

    state.clamp(TARGET_MIN, TARGET_MAX)
    target_int = int(round(state.difficulty_float))

    email = _pick_email(user_id, target_int)
    if not email:
        return Response({"detail": "No arcade emails available"}, status=404)

    payload = EmailSerializer(email).data
    payload["target_difficulty"] = state.difficulty_float
    payload["target_difficulty_int"] = target_int
    return Response(payload)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def post_arcade_attempt(request):
    user_id = request.user.username
    email_id = request.data.get("email_id")
    guess_is_phish = request.data.get("guess_is_phish")
    response_time_ms = request.data.get("response_time_ms", None)

    if email_id is None or guess_is_phish is None:
        return Response({"detail": "email_id and guess_is_phish required"}, status=400)

    try:
        email = Email.objects.get(id=email_id, mode="arcade")
    except Email.DoesNotExist:
        return Response({"detail": "Email not found"}, status=404)

    was_correct = (email.is_phish == bool(guess_is_phish))

    state, _ = ArcadeState.objects.get_or_create(user_id=user_id)
    state.clamp(TARGET_MIN, TARGET_MAX)
    target_before = state.difficulty_float

    # Staircase update
    state.total += 1
    if was_correct:
        state.correct += 1
        state.streak = max(0, state.streak) + 1
        state.difficulty_float += 0.30
    else:
        state.streak = min(0, state.streak) - 1
        state.difficulty_float -= 0.50

    state.clamp(TARGET_MIN, TARGET_MAX)
    state.last_email = email
    state.save()

    ArcadeAttempt.objects.create(
        user_id=user_id,
        email=email,
        guess_is_phish=bool(guess_is_phish),
        was_correct=was_correct,
        response_time_ms=response_time_ms if response_time_ms is None else int(response_time_ms),
        target_difficulty=target_before,
        email_difficulty=email.difficulty,
    )

    return Response({
        "was_correct": was_correct,
        "new_target_difficulty": state.difficulty_float,
        "accuracy": (state.correct / state.total) if state.total else 0,
    }, status=201)