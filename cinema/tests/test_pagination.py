from django.test import TestCase
from rest_framework.test import APIClient
from cinema.models import Actor


class TestPagination(TestCase):
    def setUp(self):
        self.client = APIClient()
        Actor.objects.bulk_create(
            [Actor(first_name=f"F{i}", last_name=f"L{i}") for i in range(15)]
        )

    def test_default_page_size_and_results_key(self):
        resp = self.client.get("/api/actors/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.data)
        self.assertEqual(len(resp.data["results"]), 10)

    def test_page_size_query_param(self):
        resp = self.client.get("/api/actors/?page_size=5")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("results", resp.data)
        self.assertEqual(len(resp.data["results"]), 5)
