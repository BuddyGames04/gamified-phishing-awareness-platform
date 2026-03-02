# src/backend/api/views_pvp.py
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Email
from .models_pvp import PvpEmail, PvpLevel, PvpScenario
from .serializers import EmailSerializer
from .serializers_pvp import (
    PvpEmailSerializer,
    PvpLevelSerializer,
    PvpScenarioSerializer,
)


# -------------------------
# Scenarios (owned CRUD)
# -------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pvp_scenarios_mine(request):
    qs = PvpScenario.objects.filter(owner=request.user).order_by("-created_at")
    return Response(PvpScenarioSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pvp_scenarios_create(request):
    ser = PvpScenarioSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    obj = ser.save(owner=request.user)
    return Response(PvpScenarioSerializer(obj).data, status=201)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def pvp_scenarios_detail(request, scenario_id: int):
    try:
        obj = PvpScenario.objects.get(id=scenario_id, owner=request.user)
    except PvpScenario.DoesNotExist:
        return Response({"detail": "Scenario not found"}, status=404)

    if request.method == "DELETE":
        obj.delete()
        return Response(status=204)

    ser = PvpScenarioSerializer(obj, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    obj = ser.save()
    return Response(PvpScenarioSerializer(obj).data)


# -------------------------
# Levels (owned CRUD + publish)
# -------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pvp_levels_mine(request):
    qs = (
        PvpLevel.objects.filter(owner=request.user)
        .select_related("scenario")
        .order_by("-created_at")
    )
    return Response(PvpLevelSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pvp_levels_posted(request):
    # Auth-only for now. If you want public later, remove permission decorator.
    qs = (
        PvpLevel.objects.filter(visibility="posted")
        .select_related("scenario")
        .order_by("-created_at")
    )
    return Response(PvpLevelSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pvp_levels_create(request):
    data = dict(request.data)
    scenario_id = request.data.get("scenario_id")

    if not scenario_id:
        return Response({"detail": "scenario_id required"}, status=400)

    try:
        scenario = PvpScenario.objects.get(id=int(scenario_id), owner=request.user)
    except (PvpScenario.DoesNotExist, ValueError):
        return Response({"detail": "Scenario not found"}, status=404)

    # IMPORTANT: always start unlisted; publishing must go through /publish/
    data["visibility"] = "unlisted"

    ser = PvpLevelSerializer(data=data)
    ser.is_valid(raise_exception=True)

    obj = ser.save(owner=request.user, scenario=scenario)
    return Response(PvpLevelSerializer(obj).data, status=201)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def pvp_levels_detail(request, level_id: int):
    try:
        lvl = PvpLevel.objects.select_related("scenario").get(
            id=level_id, owner=request.user
        )
    except PvpLevel.DoesNotExist:
        return Response({"detail": "Level not found"}, status=404)

    if request.method == "DELETE":
        # delete shadow Email rows for all emails in this level
        shadow_ids = list(
            PvpEmail.objects.filter(level=lvl)
            .exclude(shadow_email__isnull=True)
            .values_list("shadow_email_id", flat=True)
        )
        lvl.delete()
        if shadow_ids:
            Email.objects.filter(id__in=shadow_ids).delete()
        return Response(status=204)

    # Block visibility changes to posted here — must use /publish/
    if "visibility" in request.data and str(request.data.get("visibility")) == "posted":
        return Response({"detail": "Use /publish/ to post a level."}, status=400)

    ser = PvpLevelSerializer(lvl, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    lvl = ser.save()
    return Response(PvpLevelSerializer(lvl).data)


def _validate_publish_constraints(level: PvpLevel):
    # email count 5..20 total
    total = PvpEmail.objects.filter(level=level).count()
    if total < 5 or total > 20:
        return f"Level must have 5–20 emails (currently {total})."

    phish = PvpEmail.objects.filter(level=level, is_phish=True).count()
    legit = PvpEmail.objects.filter(level=level, is_phish=False).count()
    if phish < 1 or legit < 1:
        return "Level must include at least 1 phishing email and 1 legitimate email."

    return None


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def pvp_levels_publish(request, level_id: int):
    try:
        lvl = PvpLevel.objects.get(id=level_id, owner=request.user)
    except PvpLevel.DoesNotExist:
        return Response({"detail": "Level not found"}, status=404)

    msg = _validate_publish_constraints(lvl)
    if msg:
        return Response({"detail": msg}, status=400)

    lvl.visibility = "posted"
    lvl.save(update_fields=["visibility"])
    return Response(PvpLevelSerializer(lvl).data)


# -------------------------
# Emails (CRUD inside a level)
# -------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pvp_level_emails_list(request, level_id: int):
    # owner-only list (even if posted)
    try:
        lvl = PvpLevel.objects.get(id=level_id, owner=request.user)
    except PvpLevel.DoesNotExist:
        return Response({"detail": "Level not found"}, status=404)

    qs = PvpEmail.objects.filter(level=lvl).order_by("is_wave", "sort_order", "id")
    return Response(PvpEmailSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pvp_level_emails_create(request, level_id: int):
    try:
        lvl = PvpLevel.objects.get(id=level_id, owner=request.user)
    except PvpLevel.DoesNotExist:
        return Response({"detail": "Level not found"}, status=404)

    ser = PvpEmailSerializer(data=request.data)
    ser.is_valid(raise_exception=True)

    em = ser.save(level=lvl)
    try:
        em.full_clean()
    except DjangoValidationError as e:
        return Response(e.message_dict, status=400)
    em.save()
    return Response(PvpEmailSerializer(em).data, status=201)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
@transaction.atomic
def pvp_level_emails_detail(request, level_id: int, email_id: int):
    try:
        lvl = PvpLevel.objects.get(id=level_id, owner=request.user)
    except PvpLevel.DoesNotExist:
        return Response({"detail": "Level not found"}, status=404)

    try:
        em = PvpEmail.objects.get(id=email_id, level=lvl)
    except PvpEmail.DoesNotExist:
        return Response({"detail": "Email not found"}, status=404)

    if request.method == "DELETE":
        sid = em.shadow_email_id
        em.delete()
        if sid:
            Email.objects.filter(id=sid).delete()
        return Response(status=204)

    ser = PvpEmailSerializer(em, data=request.data, partial=True)
    ser.is_valid(raise_exception=True)
    em = ser.save()
    try:
        em.full_clean()
    except DjangoValidationError as e:
        return Response(e.message_dict, status=400)
    em.save()
    return Response(PvpEmailSerializer(em).data)


# -------------------------
# Play endpoint (InboxView) — returns shadow Email rows
# -------------------------


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pvp_play_emails(request):
    """
    Returns real Email rows (shadow copies) so the frontend can reuse the existing
    EmailSerializer shape without special-casing PVP.

    Rules:
    - Can play if the level is posted OR the requester is the owner.
    - Supports ?wave=true|false and ?limit=N.
    """
    level_id = request.query_params.get("level_id")
    if not level_id:
        return Response({"detail": "level_id required"}, status=400)

    try:
        lvl_id_int = int(level_id)
    except ValueError:
        return Response({"detail": "level_id must be an integer"}, status=400)

    limit = int(request.query_params.get("limit", "20"))
    wave_true = str(request.query_params.get("wave", "")).lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
    )

    # Can play if posted OR owner
    lvl = (
        PvpLevel.objects.select_related("scenario")
        .filter(id=lvl_id_int)
        .filter(Q(visibility="posted") | Q(owner=request.user))
        .first()
    )
    if not lvl:
        return Response({"detail": "Level not found"}, status=404)

    # PvpEmail rows in the correct order for this wave state
    pvp_qs = (
        PvpEmail.objects.filter(level=lvl, is_wave=wave_true)
        .order_by("sort_order", "id")[:limit]
    )

    # Ensure shadow emails exist and preserve order
    shadow_ids: list[int] = []
    for pe in pvp_qs:
        sid = getattr(pe, "shadow_email_id", None)
        if sid is None:
            if hasattr(pe, "sync_shadow_email") and callable(pe.sync_shadow_email):
                pe.sync_shadow_email()
                sid = getattr(pe, "shadow_email_id", None)

        if sid is not None:
            shadow_ids.append(int(sid))

    if not shadow_ids:
        return Response([], status=200)

    shadows = Email.objects.filter(id__in=shadow_ids)
    shadows_by_id = {e.id: e for e in shadows}
    ordered = [shadows_by_id[sid] for sid in shadow_ids if sid in shadows_by_id]

    return Response(EmailSerializer(ordered, many=True).data)