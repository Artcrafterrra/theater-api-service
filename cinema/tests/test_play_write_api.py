from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from cinema.models import Actor, Genre, Play


class TestPlayWriteAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin", password="pass", is_staff=True, is_superuser=True
        )
        self.a1 = Actor.objects.create(first_name="Tom", last_name="Hardy")
        self.a2 = Actor.objects.create(first_name="Emily", last_name="Blunt")
        self.g1 = Genre.objects.create(name="Drama")
        self.g2 = Genre.objects.create(name="Thriller")

    def test_create_play_accepts_ids_and_read_returns_nested(self):
        self.client.force_authenticate(self.admin)
        payload = {
            "title": "New Play",
            "description": "Desc",
            "actors": [self.a1.id, self.a2.id],
            "genres": [self.g1.id, self.g2.id],
        }
        resp = self.client.post("/api/plays/", payload, format="json")
        self.assertEqual(resp.status_code, 201)
        play_id = resp.data["id"]
        resp2 = self.client.get(f"/api/plays/{play_id}/")
        self.assertEqual(resp2.status_code, 200)
        self.assertIsInstance(resp2.data["actors"], list)
        self.assertIsInstance(resp2.data["genres"], list)
        self.assertEqual({a["id"] for a in resp2.data["actors"]}, {self.a1.id, self.a2.id})
        self.assertEqual({g["id"] for g in resp2.data["genres"]}, {self.g1.id, self.g2.id})

    def test_partial_update_works_with_create_update_serializer(self):
        self.client.force_authenticate(self.admin)
        play = Play.objects.create(title="Edit Me")
        resp = self.client.patch(
            f"/api/plays/{play.id}/",
            {"actors": [self.a1.id]},
            format="json",
        )
        self.assertIn(resp.status_code, (200, 202))
        play.refresh_from_db()
        self.assertEqual(list(play.actors.values_list("id", flat=True)), [self.a1.id])