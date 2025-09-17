from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class TestPermissionsNonAdmin(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pass")

    def test_non_admin_cannot_modify(self):
        self.client.force_authenticate(self.user)
        resp = self.client.post("/api/genres/", {"name": "Sci-Fi"}, format="json")
        self.assertEqual(resp.status_code, 403)