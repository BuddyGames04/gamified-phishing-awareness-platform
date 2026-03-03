from rest_framework.test import APITestCase

from api.models import EmailDecisionEvent, InteractionEvent, LevelRun
from .helpers import make_authed_client


class TestDecisionsAndInteractions(APITestCase):
    def setUp(self):
        self.client, self.user = make_authed_client()

    def test_create_interaction_event(self):
        # Assumes /api/interaction/ exists and accepts: user_id, email_id, event_type, value
        res = self.client.post(
            "/api/interaction/",
            {
                "user_id": self.user.username,
                "email_id": 1,
                "event_type": "link_click",
                "value": "http://example.com",
            },
            format="json",
        )
        self.assertIn(res.status_code, (200, 201), getattr(res, "data", None))
        self.assertTrue(
            InteractionEvent.objects.filter(user_id=self.user.username, email=1).exists()
        )

    def test_create_decision_event(self):
        # create a run (some implementations require run_id nullable; your frontend passes run_id)
        run = LevelRun.objects.create(
            user_id=self.user.username,
            mode="simulation",
            scenario=None,
            level_number=1,
            emails_total=5,
        )

        res = self.client.post(
            "/api/metrics/decisions/",
            {
                "user_id": self.user.username,
                "run_id": run.id,
                "email_id": 1,
                "decision": "report_phish",
                "was_correct": True,
            },
            format="json",
        )
        self.assertIn(res.status_code, (200, 201), getattr(res, "data", None))
        self.assertTrue(
            EmailDecisionEvent.objects.filter(user_id=self.user.username, run=run, email_id=1).exists()
        )