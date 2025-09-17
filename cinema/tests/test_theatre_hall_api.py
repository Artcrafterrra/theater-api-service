from django.test import TestCase
from rest_framework.test import APIClient
from cinema.models import TheatreHall


class TestTheatreHallAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.h1 = TheatreHall.objects.create(name="Blue", rows=5, seats_in_row=6)

    def _extract(self, resp):
        return resp.data["results"] if isinstance(resp.data, dict) and "results" in resp.data else resp.data

    def test_list_includes_capacity(self):
        resp = self.client.get("/api/halls/")
        self.assertEqual(resp.status_code, 200)
        data = self._extract(resp)
        self.assertTrue(len(data) >= 1)
        item = data[0]
        self.assertIn("capacity", item)
        self.assertEqual(item["capacity"], self.h1.rows * self.h1.seats_in_row)

    def test_retrieve_includes_capacity_correct_value(self):
        resp = self.client.get(f"/api/halls/{self.h1.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("capacity", resp.data)
        self.assertEqual(resp.data["capacity"], self.h1.rows * self.h1.seats_in_row)