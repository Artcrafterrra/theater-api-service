from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from cinema.models import TheatreHall, Play, Performance

import cinema.signals  # noqa: F401


class TestPerformanceAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.hall = TheatreHall.objects.create(
            name="Blue", rows=5, seats_in_row=6
        )
        self.play = Play.objects.create(title="Edge of Stage")
        self.perf = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=timezone.now()
        )

    def test_retrieve_returns_nested_read_serializer(self):
        resp = self.client.get(f"/api/performances/{self.perf.id}/")
        self.assertEqual(resp.status_code, 200)
        data = resp.data

        self.assertIn("play", data)
        self.assertIn("theatre_hall", data)

        self.assertIsInstance(data["play"], dict)
        self.assertIn("title", data["play"])
        self.assertIn("actors", data["play"])
        self.assertIsInstance(data["play"]["actors"], list)
        self.assertIn("genres", data["play"])
        self.assertIsInstance(data["play"]["genres"], list)

        self.assertIsInstance(data["theatre_hall"], dict)
        self.assertIn("name", data["theatre_hall"])
        self.assertIn("rows", data["theatre_hall"])
        self.assertIn("seats_in_row", data["theatre_hall"])
        self.assertIn("capacity", data["theatre_hall"])
        self.assertEqual(
            data["theatre_hall"]["capacity"],
            self.hall.rows * self.hall.seats_in_row,
        )
