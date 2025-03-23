from django.test import TestCase
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework.test import APIClient

class TestAtendimentoAPI(TestCase):
    def setUp(self):
        self.client_api = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_api_unauthenticated_get(self):
        url = reverse("atendimento-create-list")
        response = self.client_api.get(url)
        # Expect unauthorized access for unauthenticated users
        self.assertIn(response.status_code, [401, 403])

    def test_api_authenticated_get(self):
        self.client_api.force_authenticate(user=self.user)
        url = reverse("atendimento-create-list")
        response = self.client_api.get(url)
        # Expect an OK response (empty list) from authenticated users
        self.assertEqual(response.status_code, 200)