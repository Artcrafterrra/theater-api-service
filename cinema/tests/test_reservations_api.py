from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from cinema.models import TheatreHall, Play, Performance, Ticket, Reservation

import cinema.signals  # noqa: F401


class TestReservationsAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", password="pass")
        self.other = User.objects.create_user(username="u2", password="pass")
        self.hall = TheatreHall.objects.create(
            name="H1", rows=3, seats_in_row=4
        )
        self.play = Play.objects.create(title="Play 1")
        self.perf = Performance.objects.create(
            play=self.play, theatre_hall=self.hall, show_time=timezone.now()
        )

    def test_create_reservation_success_and_ticket_association(self):
        self.client.force_authenticate(self.user)
        payload = {
            "performance": self.perf.id,
            "seats": [{"row": 1, "seat": 1}, {"row": 2, "seat": 3}],
        }
        resp = self.client.post("/api/reservations/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.data
        self.assertIn("id", data)
        self.assertIn("created_at", data)
        self.assertIn("tickets", data)
        self.assertEqual(len(data["tickets"]), 2)

        reservation = Reservation.objects.get(id=data["id"])
        for pair in [(1, 1), (2, 3)]:
            t = Ticket.objects.get(
                performance=self.perf, row=pair[0], seat=pair[1]
            )
            self.assertEqual(t.reservation_id, reservation.id)

    def test_create_reservation_duplicate_seats_validation(self):
        self.client.force_authenticate(self.user)
        payload = {
            "performance": self.perf.id,
            "seats": [{"row": 1, "seat": 1}, {"row": 1, "seat": 1}],
        }
        resp = self.client.post("/api/reservations/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Duplicate seats", str(resp.data))

    def test_create_reservation_out_of_bounds_validation(self):
        self.client.force_authenticate(self.user)
        payload = {
            "performance": self.perf.id,
            "seats": [{"row": 1, "seat": 5}],
        }
        resp = self.client.post("/api/reservations/", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn("out of hall bounds", str(resp.data))

    def test_create_reservation_conflict_when_already_reserved(self):
        self.client.force_authenticate(self.user)
        payload = {
            "performance": self.perf.id,
            "seats": [{"row": 1, "seat": 1}],
        }
        resp = self.client.post("/api/reservations/", payload, format="json")
        self.assertEqual(resp.status_code, 201)

        self.client.force_authenticate(self.other)
        resp2 = self.client.post("/api/reservations/", payload, format="json")
        self.assertEqual(resp2.status_code, 400)
        self.assertIn("already reserved", str(resp2.data))

    def test_list_shows_only_current_user_reservations_and_paginated(self):
        self.client.force_authenticate(self.user)
        self.client.post(
            "/api/reservations/",
            {"performance": self.perf.id, "seats": [{"row": 1, "seat": 2}]},
            format="json",
        )
        self.client.force_authenticate(self.other)
        self.client.post(
            "/api/reservations/",
            {"performance": self.perf.id, "seats": [{"row": 1, "seat": 3}]},
            format="json",
        )

        self.client.force_authenticate(self.user)
        resp = self.client.get("/api/reservations/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data, dict)
        self.assertIn("results", resp.data)
        for item in resp.data["results"]:
            self.assertIn("tickets", item)
            self.assertTrue(
                all("row" in t and "seat" in t for t in item["tickets"])
            )
