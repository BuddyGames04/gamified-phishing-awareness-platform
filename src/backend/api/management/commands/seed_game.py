from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from api.management.seeders.scenarios import seed_scenarios_and_simulation_emails
from api.models import Email, Level, LevelEmail, Scenario


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--wipe", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        wipe = bool(options.get("wipe"))

        if wipe:
            LevelEmail.objects.all().delete()
            Level.objects.all().delete()
            Email.objects.all().delete()
            Scenario.objects.all().delete()

        seed_scenarios_and_simulation_emails(stdout=self.stdout, style=self.style)

        call_command("seed_levels_1_5")
        call_command("seed_levels_6_10")
        call_command("seed_arcade")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        self.stdout.write(f"- Scenarios: {Scenario.objects.count()}")
        self.stdout.write(f"- Simulation emails: {Email.objects.filter(mode='simulation').count()}")
        self.stdout.write(f"- Arcade emails: {Email.objects.filter(mode='arcade').count()}")