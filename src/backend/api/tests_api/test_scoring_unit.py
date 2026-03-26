from django.test import TestCase
from api.scoring import base_points


class TestScoringUnit(TestCase):
    def test_base_points_punishes_wrong_more_than_right(self):
        self.assertEqual(base_points(1, 0), 100)
        self.assertEqual(base_points(0, 1), 0)               
        self.assertEqual(base_points(3, 1), 120)             

    def test_base_points_floor(self):
        self.assertEqual(base_points(1, 2), 0)