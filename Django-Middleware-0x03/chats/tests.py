from django.test import TestCase

# Create your tests here.
import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from chats.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from chats.models import User, Conversation
from datetime import datetime, time, timezone, timedelta
from unittest.mock import patch
from django.http import HttpResponseForbidden
import uuid


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


class OffensiveLanguageMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email="numbskull@gmail.com",
            password="12345678",
            first_name="Numb",
            last_name="Skull",
            username="numbskull@gmail.com",
        )
        self.token = RefreshToken.for_user(self.user).access_token
        self.conversation = Conversation.objects.create(
            conversation_id=uuid.uuid4(), name="Test Chat"
        )
        self.conversation.participants.add(self.user)
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.truncate()
        # Clear in-memory message counts
        from chats.middleware import message_counts

        message_counts.clear()

    @patch("chats.middleware.datetime")
    def test_message_limit_within_window(self, mock_datetime):
        """Test sending up to 5 messages within 1 minute"""
        base_time = datetime(2025, 6, 7, 17, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        for i in range(5):
            response = self.client.post(
                reverse("message-list"),
                {
                    "conversation": str(self.conversation.conversation_id),
                    "message_body": f"Test message {i+1}",
                    "message_type": "TEXT",
                },
                format="json",
            )
            self.assertEqual(response.status_code, 201)
        # Sixth message should be blocked
        response = self.client.post(
            reverse("message-list"),
            {
                "conversation": str(self.conversation.conversation_id),
                "message_body": "Test message 6",
                "message_type": "TEXT",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.content.decode(),
            "Message limit exceeded: 5 messages per minute allowed.",
        )
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertEqual(logs.count("/api/messages/"), 6)

    @patch("chats.middleware.datetime")
    def test_message_limit_reset_after_window(self, mock_datetime):
        """Test limit resets after 1 minute"""
        base_time = datetime(2025, 6, 7, 17, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = base_time
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # Send 5 messages
        for i in range(5):
            response = self.client.post(
                reverse("message-list"),
                {
                    "conversation": str(self.conversation.conversation_id),
                    "message_body": f"Test message {i+1}",
                    "message_type": "TEXT",
                },
                format="json",
            )
            self.assertEqual(response.status_code, 201)
        # Advance time by 61 seconds
        mock_datetime.now.return_value = base_time + timedelta(seconds=61)
        # Send another message
        response = self.client.post(
            reverse("message-list"),
            {
                "conversation": str(self.conversation.conversation_id),
                "message_body": "Test message 6",
                "message_type": "TEXT",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 201)

    def test_non_post_requests_unaffected(self):
        """Test GET requests are not rate-limited"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        for i in range(10):
            response = self.client.get(reverse("message-list"))
            self.assertNotEqual(response.status_code, 429)
