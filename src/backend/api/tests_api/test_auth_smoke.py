from rest_framework.test import APITestCase, APIClient


class TestAuthSmoke(APITestCase):
    def setUp(self):
        self.client = APIClient()  # no credentials

    def test_leaderboard_requires_auth(self):
        # If leaderboard is public, change expected code to 200.
        res = self.client.get("/api/leaderboard/?mode=overall&sort=desc")
        self.assertIn(res.status_code, (401, 403), getattr(res, "data", None))

    def test_arcade_next_requires_auth(self):
        res = self.client.get("/api/arcade/next/")
        self.assertIn(res.status_code, (401, 403), getattr(res, "data", None))