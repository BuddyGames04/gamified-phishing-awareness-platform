from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from api.management.seeders.arcade import seed_arcade_emails


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        created = seed_arcade_emails()
        self.stdout.write(self.style.SUCCESS(f"Seeded arcade emails (+{created})."))
