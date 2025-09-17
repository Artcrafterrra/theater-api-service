from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient


class TestStaffWriteReadOnlyElse(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.admin = User.objects.create_user(
            username="admin",
            password="adminpass",
            is_staff=True,
            is_superuser=True,
        )

    def test_read_allowed_for_anonymous(self):
        resp = self.client.get("/api/actors/")
        self.assertIn(resp.status_code, (200, 204))
        resp = self.client.post(
            "/api/actors/",
            {"first_name": "A", "last_name": "B"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_write_allowed_for_admin(self):
        self.client.force_authenticate(self.admin)
        resp = self.client.post(
            "/api/actors/",
            {"first_name": "A", "last_name": "B"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
