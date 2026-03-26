from rest_framework.test import APITestCase
from .helpers import make_authed_client

from api.models import ArcadeAttempt


class TestArcade(APITestCase):
    def setUp(self):
        self.client, self.user = make_authed_client()

    def test_arcade_next_returns_email_payload(self):
        res = self.client.get("/api/arcade/next/")
        self.assertEqual(res.status_code, 200, res.data)

        self.assertIn("id", res.data)
        self.assertIn("subject", res.data)
        self.assertIn("body", res.data)
        self.assertIn("is_phish", res.data)

    def test_arcade_attempt_creates_attempt_and_returns_hint_fields(self):
        next_res = self.client.get("/api/arcade/next/")
        self.assertEqual(next_res.status_code, 200, next_res.data)
        email_id = next_res.data["id"]
        guess_is_phish = bool(next_res.data["is_phish"])

        res = self.client.post(
            "/api/arcade/attempt/",
            {
                "email_id": email_id,
                "guess_is_phish": guess_is_phish,
                "response_time_ms": 1234,
            },
            format="json",
        )
        self.assertIn(res.status_code, (200, 201), res.data)

        self.assertIn("was_correct", res.data)
        self.assertIn("new_target_difficulty", res.data)
        self.assertIn("accuracy", res.data)

        self.assertTrue(
            ArcadeAttempt.objects.filter(user_id=self.user.username, email_id=email_id).exists()
        )