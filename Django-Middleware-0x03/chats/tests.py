from django.test import TestCase

# Create your tests here.
import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from chats.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, time, timezone
from unittest.mock import patch
from django.http import HttpResponseForbidden


class RestrictAccessByTimeMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email="numbskull@gmail.com",
            password="12345678",
            first_name="Numb",
            last_name="Skull",
            username="numbskull@gmail.com",
            # username="superuser123",
        )
        self.token = RefreshToken.for_user(self.user).access_token
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.truncate()

    @patch("chats.middleware.datetime")
    def test_access_allowed_during_hours(self, mock_datetime):
        """Test access is allowed between 6 PM and 9 PM"""
        # Mock time to 7 PM
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("message-list"))
        self.assertNotEqual(response.status_code, 403)  # Should not be forbidden
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertIn(f"User: numbskull@gmail.com - Path: /api/messages/", logs)

    @patch("chats.middleware.datetime")
    def test_access_denied_outside_hours(self, mock_datetime):
        """Test access is denied outside 6 PM to 9 PM"""
        # Mock time to 4 PM
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 16, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("message-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(),
            "Access restricted outside allowed hours (6pm to 9pm).",
        )
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertIn(f"User: numbskull@gmail.com - Path: /api/messages/", logs)

    @patch("chats.middleware.datetime")
    def test_unauthenticated_access_denied_outside_hours(self, mock_datetime):
        """Test unauthenticated access is denied outside hours"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 16, 0, 0, tzinfo=timezone.utc
        )
        response = self.client.get(reverse("message-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(),
            "Access restricted outside allowed hours (6pm to 9pm).",
        )
