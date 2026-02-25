import re
from urllib.parse import urlparse

from rest_framework import serializers

from .models_pvp import PvpEmail, PvpLevel, PvpScenario

# allow letters/numbers/._- and require an extension like ".pdf"
FILENAME_RE = re.compile(r"^[A-Za-z0-9._-]+\.[A-Za-z0-9]{2,8}$")


class PvpScenarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PvpScenario
        fields = [
            "id",
            "name",
            "company_name",
            "sector",
            "role_title",
            "department_name",
            "line_manager_name",
            "responsibilities",
            "intro_text",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class PvpLevelSerializer(serializers.ModelSerializer):
    scenario_id = serializers.IntegerField(write_only=True, required=False)
    scenario = PvpScenarioSerializer(read_only=True)

    class Meta:
        model = PvpLevel
        fields = [
            "id",
            "scenario",
            "scenario_id",
            "title",
            "briefing",
            "visibility",
            "plays",
            "avg_accuracy",
            "created_at",
        ]
        read_only_fields = ["id", "plays", "avg_accuracy", "created_at", "scenario"]


class PvpEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PvpEmail
        fields = [
            "id",
            "sender_name",
            "sender_email",
            "subject",
            "body",
            "is_phish",
            "difficulty",
            "category",
            "links",
            "attachments",
            "is_wave",
            "sort_order",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        def tidy(s):
            return (s or "").strip()

        def tidy_space(s):
            return " ".join(tidy(s).split())

        def tidy_list(xs):
            if xs is None:
                return []
            if isinstance(xs, str):
                xs = [xs]
            if not isinstance(xs, list):
                xs = [xs]
            return [str(x).strip() for x in xs if str(x).strip()]

        # ---- normalise basic fields (only if provided) ----
        if "sender_name" in attrs:
            attrs["sender_name"] = tidy_space(attrs.get("sender_name"))
            if len(attrs["sender_name"]) < 2:
                raise serializers.ValidationError(
                    {"sender_name": "Sender name is too short."}
                )

        if "sender_email" in attrs:
            attrs["sender_email"] = tidy(attrs.get("sender_email")).lower()

        if "subject" in attrs:
            attrs["subject"] = tidy_space(attrs.get("subject"))
            if len(attrs["subject"]) < 3:
                raise serializers.ValidationError({"subject": "Subject is too short."})

        if "body" in attrs:
            if len(tidy(attrs["body"])) < 10:
                raise serializers.ValidationError(
                    {"body": "Body must be at least 10 characters."}
                )

        if "category" in attrs:
            cat = attrs.get("category")
            attrs["category"] = tidy_space(cat) if cat else None

        # ---- difficulty ----
        if "difficulty" in attrs:
            try:
                d = int(attrs["difficulty"])
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {"difficulty": "Difficulty must be a number."}
                )
            if d < 1 or d > 5:
                raise serializers.ValidationError(
                    {"difficulty": "Difficulty must be between 1 and 5."}
                )
            attrs["difficulty"] = d

        # ---- list fields (PATCH-safe: only touch if present) ----
        if "links" in attrs:
            attrs["links"] = tidy_list(attrs.get("links"))

        if "attachments" in attrs:
            attrs["attachments"] = [
                f.replace(" ", "_") for f in tidy_list(attrs.get("attachments"))
            ]

        # ---- determine final state for XOR (PATCH-safe) ----
        links = attrs.get("links", None)
        attachments = attrs.get("attachments", None)

        if self.instance:
            final_links = links if links is not None else (self.instance.links or [])
            final_attachments = (
                attachments
                if attachments is not None
                else (self.instance.attachments or [])
            )
        else:
            final_links = links or []
            final_attachments = attachments or []

        has_links = len(final_links) > 0
        has_attachments = len(final_attachments) > 0

        if has_links and has_attachments:
            raise serializers.ValidationError(
                {
                    "links": "Choose either links or attachments (not both).",
                    "attachments": "Choose either links or attachments (not both).",
                }
            )
        if not has_links and not has_attachments:
            raise serializers.ValidationError(
                {
                    "links": "Provide at least one link or one attachment.",
                    "attachments": "Provide at least one link or one attachment.",
                }
            )

        # ---- link validation ----
        if has_links:
            if len(final_links) > 5:
                raise serializers.ValidationError({"links": "Maximum 5 links allowed."})
            for u in final_links:
                p = urlparse(u)
                if (
                    p.scheme not in ("http", "https")
                    or not p.netloc
                    or "." not in p.netloc
                ):
                    raise serializers.ValidationError({"links": f"Invalid URL: {u}"})

        # ---- attachment validation ----
        if has_attachments:
            if len(final_attachments) > 5:
                raise serializers.ValidationError(
                    {"attachments": "Maximum 5 attachments allowed."}
                )
            for f in final_attachments:
                if not FILENAME_RE.match(f):
                    raise serializers.ValidationError(
                        {"attachments": f"Invalid filename: {f} (example: invoice.pdf)"}
                    )

        return attrs
