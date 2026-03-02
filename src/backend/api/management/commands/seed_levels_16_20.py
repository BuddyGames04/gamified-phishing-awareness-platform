from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from api.management.seeders.curated_16_20 import curated_levels_16_20
from api.management.seeders.levels import apply_curated_level_defs
from api.models import Scenario


class Command(BaseCommand):
    help = (
        "Seed curated simulation levels 16–20 (handmade). Safe to run multiple times."
    )

    @transaction.atomic
    def handle(self, *args, **options):
        scenario_by_company = {s.company_name: s for s in Scenario.objects.all()}
        defs = curated_levels_16_20(scenario_by_company)
        apply_curated_level_defs(defs)
        self.stdout.write(self.style.SUCCESS("Seeded curated levels 16–20."))
