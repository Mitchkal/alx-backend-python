from django.test import TestCase

# Create your tests here.
import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from chats.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from chats.models import User, Conversation, Message, Notification
from datetime import datetime, time, timezone, timedelta
from unittest.mock import patch
from django.http import HttpResponseForbidden
import uuid
import json


class RestrictAccessByTimeMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email="numbskull@gmail.com",
            password="12345678",
            first_name="Numb",
            last_name="Skull",
            # username="numbskull@gmail.com",
            username="superuser123",
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
        self.assertIn(f"User: superuser123 - Path: /api/messages/", logs)

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
        self.assertIn(f"User: superuser123 - Path: /api/messages/", logs)

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
            username="superuser123",
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
                    "content": f"Test message {i+1}",
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
                "content": "Test message 6",
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
                    "content": f"Test message {i+1}",
                    "message_type": "TEXT",
                },
                format="json",
            )
            # print(f"message limit reset response is: {response.data}")
            self.assertEqual(response.status_code, 201)
        # Advance time by 61 seconds
        mock_datetime.now.return_value = base_time + timedelta(seconds=61)
        # Send another message
        response = self.client.post(
            reverse("message-list"),
            {
                "conversation": str(self.conversation.conversation_id),
                "content": "Test message 6",
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


class RootUrlTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("chats.middleware.datetime")
    def test_root_url(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2025, 6, 12, 19, 0, 0, tzinfo=timezone.utc
        )
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Welcome to the Messaging App", response.content.decode())


class NotificationSignalTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="Pass123!",
            first_name="John",
            last_name="Doe",
            username="user1",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="Pass123!",
            first_name="Jane",
            last_name="Doe",
            username="user2",
        )
        self.token1 = RefreshToken.for_user(self.user1).access_token
        self.token2 = RefreshToken.for_user(self.user2).access_token
        self.conversation = Conversation.objects.create(
            conversation_id=uuid.uuid4(), name="Test Chat"
        )
        self.conversation.participants.add(self.user1, self.user2)
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.truncate()
        from chats.middleware import message_counts

        message_counts.clear()

    @patch("chats.middleware.datetime")
    def test_notification_created_for_direct_message(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2025, 6, 12, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")
        data = {
            "conversation_id": str(self.conversation.conversation_id),
            "receiver_id": str(self.user2.user_id),
            "sender_id": str(self.user1.user_id),
            "content": "Hello!",
            "message_type": "TEXT",
        }

        print(f"Sending data: {data}")  # Debug
        response = self.client.post(
            reverse("message-list"),
            data=json.dumps(data),
            # data,
            # format="json",
            content_type="application/json",
        )
        print(f"response data is: {response.data}")
        if response.status_code != 201:
            print(f"Response content: {response.content.decode()}")  # Debug
        self.assertEqual(
            response.status_code, 201, f"Failed with: {response.content.decode()}"
        )
        notifications = Notification.objects.filter(user=self.user2)
        self.assertEqual(notifications.count(), 1)
        notification = notifications.first()
        self.assertEqual(notification.message.content, "Hello!")
        self.assertFalse(notification.is_read)

    @patch("chats.middleware.datetime")
    def test_message_history_api(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2025, 6, 12, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token1}")
        # Create and edit a message
        data = {
            "conversation_id": str(self.conversation.conversation_id),
            "receiver_id": str(self.user2.id),
            "content": "Original message",
            "message_type": "TEXT",
        }
        response = self.client.post(reverse("message-list"), data, format="json")
        self.assertEqual(response.status_code, 201)
        message_id = response.data["message_id"]
        update_data = {"content": "Edited message"}
        self.client.patch(
            reverse("message-detail", kwargs={"pk": message_id}),
            update_data,
            format="json",
        )

        # Get history
        response = self.client.get(
            reverse("message-history", kwargs={"pk": message_id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["old_content"], "Original message")
        self.assertEqual(response.data[0]["edited_by"]["username"], "user1")


class RolePermissionMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="Pass123!",
            first_name="Admin",
            last_name="User",
            username="admin123",
        )
        self.moderator = User.objects.create_user(
            email="mod@example.com",
            password="Pass123!",
            first_name="Mod",
            last_name="User",
            username="mod123",
            is_staff=True,
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="Pass123!",
            first_name="John",
            last_name="Doe",
            username="user123",
        )
        self.admin_token = RefreshToken.for_user(self.admin).access_token
        self.moderator_token = RefreshToken.for_user(self.moderator).access_token
        self.user_token = RefreshToken.for_user(self.user).access_token
        self.conversation = Conversation.objects.create(
            conversation_id=uuid.uuid4(), name="Test Chat"
        )
        self.conversation.participants.add(self.admin)
        self.message = Message.objects.create(
            message_id=uuid.uuid4(),
            conversation=self.conversation,
            sender=self.admin,
            content="Test",
            message_type="TEXT",
        )
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.truncate()
        # Clear message counts
        from chats.middleware import message_counts

        message_counts.clear()

    @patch("chats.middleware.datetime")
    def test_admin_access_restricted_action(self, mock_datetime):
        """Test admin can access restricted actions"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )  # 7 PM
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)
        response = self.client.delete(
            reverse("message-detail", kwargs={"message_id": self.message.message_id})
        )
        self.assertEqual(response.status_code, 204)
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertIn(f"User: admin123 - Path: /api/users/", logs)

    @patch("chats.middleware.datetime")
    def test_moderator_access_restricted_action(self, mock_datetime):
        """Test moderator can access restricted actions"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.moderator_token}")
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 200)

    @patch("chats.middleware.datetime")
    def test_user_denied_restricted_action(self, mock_datetime):
        """Test regular user is denied restricted actions"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(),
            "Admin or moderator role required for this action.",
        )

    @patch("chats.middleware.datetime")
    def test_unauthenticated_denied_restricted_action(self, mock_datetime):
        """Test unauthenticated user is denied restricted actions"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )
        response = self.client.get(reverse("user-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.content.decode(), "Authentication required for this action."
        )

    @patch("chats.middleware.datetime")
    def test_user_allowed_unrestricted_action(self, mock_datetime):
        """Test regular user can access unrestricted actions"""
        mock_datetime.now.return_value = datetime(
            2025, 6, 7, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user_token}")
        response = self.client.get(reverse("message-list"))
        self.assertEqual(response.status_code, 200)


class RolePermissionMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create users
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="Pass123!",
            username="admin",
            first_name="Admin",
            last_name="User",
        )
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="Pass123!",
            username="user1",
            first_name="John",
            last_name="Doe",
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="Pass123!",
            username="user2",
            first_name="Jane",
            last_name="Doe",
        )
        # Create tokens
        self.admin_token = RefreshToken.for_user(self.admin).access_token
        self.user1_token = RefreshToken.for_user(self.user1).access_token
        # Create conversation
        self.conversation = Conversation.objects.create(
            conversation_id=uuid.uuid4(), name="Test Chat"
        )
        self.conversation.participants.add(self.user1, self.user2)
        # Create message with valid receiver and conversation
        self.message = Message.objects.create(
            message_id=uuid.uuid4(),
            conversation=self.conversation,
            sender=self.user1,
            receiver=self.user2,  # Ensure valid receiver
            content="Test message",
            message_type="TEXT",
        )
        # Clear message counts
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w") as f:
            f.truncate()
        from chats.middleware import message_counts

        message_counts.clear()

    @patch("chats.middleware.datetime")
    def test_admin_access_restricted_action(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2025, 6, 12, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
        response = self.client.delete(
            reverse("message-detail", kwargs={"pk": self.message.message_id})
        )
        self.assertEqual(response.status_code, 204)  # Admin can delete

    @patch("chats.middleware.datetime")
    def test_non_admin_access_restricted_action(self, mock_datetime):
        mock_datetime.now.return_value = datetime(
            2025, 6, 12, 19, 0, 0, tzinfo=timezone.utc
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.user1_token}")
        response = self.client.delete(
            reverse("message-detail", kwargs={"pk": self.message.message_id})
        )
        self.assertEqual(response.status_code, 403)  # Non-admin cannot delete


class RequestLoggingMiddlewareTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email="numbskull@gmail.com",
            password="Pass123!",
            first_name="Numb",
            last_name="Skull",
            username="superuser123",
        )
        self.token = RefreshToken.for_user(self.user).access_token
        self.log_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "logs", "requests.log"
        )
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        # Clear log file before tests
        with open(self.log_file, "w") as f:
            f.truncate()

    def test_logging_authenticated_request(self):
        """Test logging for authenticated requests"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        response = self.client.get(reverse("message-list"))
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertIn(f"User: superuser123 - Path: /api/messages/", logs)
        self.assertTrue(
            any(
                line.startswith(str(datetime.now().date())) for line in logs.split("\n")
            )
        )

    def test_logging_unauthenticated_request(self):
        """Test logging for unauthenticated requests"""
        response = self.client.get("/api/messages/")
        with open(self.log_file, "r") as f:
            logs = f.read()
        self.assertIn(f"AuthenticatedUser: None - Path: /api/messages/", logs)
        self.assertTrue(
            any(
                line.startswith(str(datetime.now().date())) for line in logs.split("\n")
            )
        )
