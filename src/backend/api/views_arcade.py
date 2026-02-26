import random
import re
from urllib.parse import urlparse

from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Email, ArcadeAttempt, ArcadeState
from .serializers import EmailSerializer


RECENT_WINDOW = 25  # don’t repeat last N
TARGET_MIN = 1.0
TARGET_MAX = 5.0  # Email.difficulty is 1..5


# -------------------------
# Hint analysis regex rules
# -------------------------
URGENCY_RE = re.compile(
    r"\b("
    r"urgent|immediately|asap|verify now|action required|final warning|account locked|"
    r"within 24 hours|avoid restriction|suspended|overdue|past due|"
    r"open attachment|open the attachment|open attached|attachment required|"
    r"last chance|today only"
    r")\b",
    re.IGNORECASE,
)
GENERIC_GREETING_RE = re.compile(
    r"\b(dear (customer|user)|dear client|hello customer)\b",
    re.IGNORECASE,
)
CRED_RE = re.compile(
    r"\b(password|passcode|login|sign in|verify your account|mfa|one-time code)\b",
    re.IGNORECASE,
)
RISKY_EXT_RE = re.compile(
    r"\.(exe|js|bat|cmd|scr|msi|ps1|vbs|jar|docm|xlsm|pptm|zip|rar)\b",
    re.IGNORECASE,
)

# Arcade hints: only these rules are shown in Arcade mode
# (Excludes educational-only and intermediate/advanced rules)
ARCADE_ALLOWED_HINTS = {
    "basic.sender",
    "basic.urgency",
    "basic.language",
    "basic.links",
    "basic.attachments",
    "phish.definition",
    "phish.social-engineering",
}


# -------------------------
# Helper functions
# -------------------------

def _domain_of_email(addr: str) -> str:
    addr = (addr or "").strip().lower()
    if "@" not in addr:
        return ""
    return addr.split("@", 1)[1]


def _domain_of_url(u: str) -> str:
    try:
        p = urlparse((u or "").strip())
        return (p.hostname or "").lower()
    except Exception:
        return ""


def _url_has_userinfo(u: str) -> bool:
    # classic https://legit.com@evil.com trick – username/password is split out
    try:
        p = urlparse((u or "").strip())
        return bool(p.username) or bool(p.password)
    except Exception:
        return False


def _root_domain(d: str) -> str:
    d = (d or "").lower().strip()
    if not d:
        return ""
    parts = d.split(".")
    if len(parts) < 2:
        return d
    return ".".join(parts[-2:])


def _pick_arcade_hint_rule_ids(email) -> list[str]:
    """
    Return 1–3 beginner-friendly rule IDs explaining likely red flags.
    """
    rules: list[str] = []

    sender_dom = _domain_of_email(getattr(email, "sender_email", ""))
    subject = getattr(email, "subject", "") or ""
    body = getattr(email, "body", "") or ""
    is_phish = bool(getattr(email, "is_phish", False))

    links = getattr(email, "links", None) or []
    atts = getattr(email, "attachments", None) or []

    # Sender identity (only warn when it's actually a phishing message)
    if is_phish and sender_dom and any(x in sender_dom for x in ["secure", "login", "verify", "support", "alerts"]):
        rules.append("basic.sender")

    # Urgency
    if URGENCY_RE.search(subject) or URGENCY_RE.search(body):
        rules.append("basic.urgency")

    # Generic greeting
    if GENERIC_GREETING_RE.search(body):
        rules.append("basic.language")

    # Credential bait
    if CRED_RE.search(subject) or CRED_RE.search(body):
        rules.append("intermediate.login-path")

    # Links
    if links:
        rules.append("basic.links")
        u0 = str(links[0])

        # userinfo trick
        if _url_has_userinfo(u0):
            rules.append("advanced.subtle-links")

        # sender vs link domain mismatch (check root domains)
        link_dom = _domain_of_url(u0)
        if sender_dom and link_dom:
            if _root_domain(sender_dom) != _root_domain(link_dom):
                if "basic.sender" not in rules:
                    rules.append("basic.sender")
                if "basic.links" not in rules:
                    rules.append("basic.links")

    # Attachments
    if atts:
        rules.append("basic.attachments")
        if any(RISKY_EXT_RE.search(str(a or "")) for a in atts):
            pass  # still covered by attachments rule

    # De-duplicate preserving order
    seen = set()
    out: list[str] = []
    for r in rules:
        if r not in seen:
            out.append(r)
            seen.add(r)

    # Filter against arcade-compatible hints only
    return [r for r in out if r in ARCADE_ALLOWED_HINTS][:3]


# -------------------------
# Email picker
# -------------------------

def _pick_email(user_id: str, target_d: int):
    recent_ids = list(
        ArcadeAttempt.objects.filter(user_id=user_id)
        .values_list("email_id", flat=True)[:RECENT_WINDOW]
    )

    candidates = Email.objects.filter(mode="arcade").exclude(id__in=recent_ids)

    exact = candidates.filter(difficulty=target_d)
    if exact.exists():
        return exact.order_by("?").first()

    band = candidates.filter(
        difficulty__in=[max(1, target_d - 1), min(5, target_d + 1)]
    )
    if band.exists():
        return band.order_by("?").first()

    fallback = Email.objects.filter(mode="arcade", difficulty=target_d)
    if fallback.exists():
        return fallback.order_by("?").first()

    return Email.objects.filter(mode="arcade").order_by("?").first()


# -------------------------
# API Endpoints
# -------------------------

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

    was_correct = email.is_phish == bool(guess_is_phish)

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
        response_time_ms=(
            response_time_ms if response_time_ms is None else int(response_time_ms)
        ),
        target_difficulty=target_before,
        email_difficulty=email.difficulty,
    )

    # -------------------------
    # Hint logic
    # -------------------------

    hint_rule_ids = []
    hint_title = None

    if not was_correct:
        # Missed a phish
        if email.is_phish and not bool(guess_is_phish):
            hint_title = "Hint: what you might have missed"
            hint_rule_ids = _pick_arcade_hint_rule_ids(email)

        # False alarm
        elif (not email.is_phish) and bool(guess_is_phish):
            hint_title = "Hint: avoiding false alarms"
            hint_rule_ids = ["intermediate.workflow", "intermediate.secondary-channel"]

    return Response(
        {
            "was_correct": was_correct,
            "new_target_difficulty": state.difficulty_float,
            "accuracy": (state.correct / state.total) if state.total else 0,
            "hint_title": hint_title,
            "hint_rule_ids": hint_rule_ids,
        },
        status=201,
    )