from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class TestLoginViews(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password = "password123"
        self.user = User.objects.create_user(username=self.username, password=self.password)

    def test_login_page_GET(self):
        url = reverse("login")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_POST_valid(self):
        url = reverse("login")
        response = self.client.post(url, {"username": self.username, "password": self.password})
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_POST_invalid(self):
        url = reverse("login")
        response = self.client.post(url, {"username": self.username, "password": "wrongpassword"})
        self.assertEqual(response.status_code, 200)  # Reloads login page
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Por favor, entre com um usuário  e senha corretos.")

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse("logout")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse(response.wsgi_request.user.is_authenticated)
