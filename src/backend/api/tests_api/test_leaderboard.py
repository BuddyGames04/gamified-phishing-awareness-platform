from rest_framework.test import APITestCase
from django.utils import timezone
from api.models import LevelRun, Scenario
from .helpers import make_authed_client

class TestLeaderboard(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.scenario = Scenario.objects.create(
            company_name="Test Co",
            sector="Test",
            role_title="Analyst",
            department_name="IT",
            line_manager_name="Boss",
            responsibilities=["a"],
            intro_text="hi",
        )

        LevelRun.objects.create(
            user_id="Alice",
            mode="simulation",
            scenario=cls.scenario,
            level_number=1,
            emails_total=5,
            correct=5,
            incorrect=0,
            points=500,
            completed_at=timezone.now(),  
        )
        LevelRun.objects.create(
            user_id="u1",
            mode="simulation",
            scenario=cls.scenario,
            level_number=3,
            emails_total=10,
            correct=5,
            incorrect=5,
            started_at=timezone.now(),
            completed_at=timezone.now(),
            duration_ms=10000,
            points=123,
        )

    def setUp(self):
        self.client, self.user = make_authed_client()

    def test_leaderboard_overall_returns_rows(self):
        res = self.client.get("/api/leaderboard/?mode=overall&sort=desc&limit=50")
        self.assertEqual(res.status_code, 200, res.data)
        ...

        self.assertIn("rows", res.data)
        rows = res.data["rows"]
        self.assertTrue(isinstance(rows, list))

        if rows:
            row0 = rows[0]
            for k in ("user_id", "score", "runs", "correct", "incorrect", "avg_duration_ms"):
                self.assertIn(k, row0)

    def test_leaderboard_simulation_sort_desc(self):
        res = self.client.get("/api/leaderboard/?mode=simulation&sort=desc&limit=10")
        self.assertEqual(res.status_code, 200, res.data)
        rows = res.data["rows"]

        if len(rows) >= 2:
            self.assertGreaterEqual(rows[0]["score"], rows[1]["score"])

    def test_leaderboard_limit(self):
        res = self.client.get("/api/leaderboard/?mode=simulation&sort=desc&limit=1")
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(len(res.data["rows"]), 1)