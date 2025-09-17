from django.test import TestCase
from rest_framework.test import APIClient
from cinema.models import Actor, Genre, Play


class TestPlayAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.actor1 = Actor.objects.create(
            first_name="Tom", last_name="Hardy"
        )
        self.actor2 = Actor.objects.create(
            first_name="Emily", last_name="Blunt"
        )
        self.genre1 = Genre.objects.create(name="Drama")
        self.genre2 = Genre.objects.create(name="Thriller")
        self.play = Play.objects.create(
            title="Edge of Stage", description="Test play"
        )
        self.play.actors.set([self.actor1, self.actor2])
        self.play.genres.set([self.genre1, self.genre2])

    def test_list_returns_nested_actors_and_genres(self):
        resp = self.client.get("/api/plays/")
        self.assertEqual(resp.status_code, 200)
        data = (
            resp.data["results"]
            if isinstance(resp.data, dict) and "results" in resp.data
            else resp.data
        )
        self.assertTrue(len(data) >= 1)
        item = data[0]
        self.assertIsInstance(item["actors"], list)
        self.assertGreaterEqual(len(item["actors"]), 2)
        self.assertIn("first_name", item["actors"][0])
        self.assertIn("last_name", item["actors"][0])

        self.assertIsInstance(item["genres"], list)
        self.assertGreaterEqual(len(item["genres"]), 2)
        self.assertIn("name", item["genres"][0])

    def test_retrieve_returns_nested(self):
        resp = self.client.get(f"/api/plays/{self.play.id}/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.data["actors"], list)
        self.assertIn("first_name", resp.data["actors"][0])
        self.assertIsInstance(resp.data["genres"], list)
        self.assertIn("name", resp.data["genres"][0])
