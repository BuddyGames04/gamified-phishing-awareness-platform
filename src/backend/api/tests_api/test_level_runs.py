from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APITestCase

from api.models import LevelRun
from .helpers import make_authed_client
from datetime import UTC


class TestLevelRuns(APITestCase):
    def setUp(self):
        self.client, self.user = make_authed_client()

    def test_start_level_run_creates_row(self):
        payload = {
            "user_id": self.user.username,
            "mode": "simulation",
            "scenario_id": 1,
            "level_number": 3,
            "emails_total": 10,
        }

        res = self.client.post("/api/metrics/level-runs/start/", payload, format="json")
        self.assertEqual(res.status_code, 201, res.data)

        run_id = res.data.get("id")
        self.assertIsNotNone(run_id)

        run = LevelRun.objects.get(id=run_id)
        self.assertEqual(run.user_id, self.user.username)
        self.assertEqual(run.mode, "simulation")
        self.assertEqual(run.level_number, 3)
        self.assertEqual(run.emails_total, 10)
        self.assertIsNotNone(run.started_at)

    @patch("django.utils.timezone.now")
    def test_complete_level_run_sets_completed_fields(self, mock_now):
        t0 = timezone.datetime(2026, 3, 2, 22, 0, 0, tzinfo=UTC)
        t1 = timezone.datetime(2026, 3, 2, 22, 1, 0, tzinfo=UTC)
        mock_now.side_effect = [t0, t1]

        res = self.client.post(
            "/api/metrics/level-runs/start/",
            {
                "user_id": self.user.username,
                "mode": "simulation",
                "scenario_id": 1,
                "level_number": 1,
                "emails_total": 5,
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201, res.data)
        run_id = res.data["id"]

        res2 = self.client.post(
            f"/api/metrics/level-runs/{run_id}/complete/",
            {
                "correct": 4,
                "incorrect": 1,
                "duration_ms": 60000,                   
                "points": 1234,
            },
            format="json",
        )
        self.assertEqual(res2.status_code, 200, getattr(res2, "data", None))

        run = LevelRun.objects.get(id=run_id)
        self.assertEqual(run.correct, 4)
        self.assertEqual(run.incorrect, 1)
        self.assertIsNotNone(run.completed_at)

        if hasattr(run, "client_duration_ms"):
            pass

        if hasattr(run, "points"):
            self.assertEqual(run.points, 1234)