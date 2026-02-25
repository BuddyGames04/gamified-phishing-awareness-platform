from __future__ import annotations

from typing import Any

from django.db import transaction

from api.management.seeders.common import clamp_difficulty
from api.models import Email, Level, LevelEmail, Scenario


@transaction.atomic
def apply_curated_level_defs(defs: list[dict[str, Any]]) -> None:
    for ld in defs:
        lvl, _ = Level.objects.update_or_create(
            scenario=ld["scenario"],
            number=ld["number"],
            defaults=dict(title=ld["title"], briefing=ld["briefing"]),
        )

        LevelEmail.objects.filter(level=lvl).delete()

        base = ld.get("emails") or ld.get("base_emails") or []
        wave = ld.get("wave_emails") or []

        def upsert_email(em: dict[str, Any]) -> Email:
            email, _ = Email.objects.update_or_create(
                mode="simulation",
                scenario=ld["scenario"],
                sender_email=em["sender_email"],
                subject=em["subject"],
                defaults=dict(
                    sender_name=em["sender_name"],
                    body=em["body"],
                    is_phish=em["is_phish"],
                    difficulty=clamp_difficulty(em.get("difficulty", 1)),
                    category=em.get("category"),
                    links=em.get("links") or [],
                    attachments=em.get("attachments") or [],
                ),
            )
            email.full_clean()
            email.save()
            return email

        for idx, em in enumerate(base):
            email = upsert_email(em)
            LevelEmail.objects.create(level=lvl, email=email, sort_order=idx)

        for widx, em in enumerate(wave):
            email = upsert_email(em)
            LevelEmail.objects.create(level=lvl, email=email, sort_order=100 + widx)