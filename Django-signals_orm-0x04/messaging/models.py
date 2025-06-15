#!/usr/bin/env python3
"""
models file
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import MessageManager


def generate_default_username():
    """
    generate default usernames
    """
    return f"user-{uuid.uuid4().hex[:8]}"


class User(AbstractUser):
    """
    user model
    """

    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    username = models.CharField(
        max_length=150, unique=True, default=generate_default_username
    )
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    status = models.CharField(max_length=100, default="Hey there! Im using ChatApp")
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    # first_name, last_name

    """
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    date_of_join = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField()
    """

    def __str__(self):
        """
        return user name
        """
        return self.email


class Conversation(models.Model):
    """
    conversations model
    """

    conversation_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False
    )

    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """
        custom save function to ccheck for
        duplicate one on one conversations
        """
        from django.db.models import Count

        if self.participants.count() == 2:
            participant_ids = sorted(
                self.participants.values_list("user_id", flat=True)
            )
            existing = (
                Conversation.objects.filter(participants__in=participant_ids)
                .annotate(num_participants=models.Count("participants"))
                .filter(num_participants=2)
            )
            if existing.exists() and not self.pk:
                raise ValueError("Conversation between these users already exists")
        super().save(*args, **kwargs)

    def last_message(self):
        """
        display most recent message in conversation list
        """
        return self.messages.order_by("-timestamp").first() or None

    def __str__(self):
        """
        return participant names in a conversation
        """
        participants = self.participants.values_list("username", flat=True)
        return f"Conversation between {','.join(participants)}"


class Message(models.Model):
    """
    model for the chat messages
    """

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    # content renamed from message_body
    content = models.TextField()
    # timestamp renamed from sent_at
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    unread = models.BooleanField(default=True)
    edited_at = models.DateTimeField(null=True)
    read_by = models.ManyToManyField(User, related_name="read_messages", blank=True)
    message_type = models.CharField(
        max_length=20,
        choices=[
            ("TEXT", "Text"),
            ("IMAGE", "Image"),
            ("FILE", "File"),
        ],
        default="TEXT",
    )
    attachment = models.FileField(upload_to="messages/", blank=True, null=True)
    # added receiver
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver", blank=True, null=True
    )
    parent_message = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    objects = MessageManager()

    class Meta:
        indexes = [
            models.Index(fields=["conversation", "timestamp"]),
        ]
        ordering = ["timestamp"]

    def clean(self):
        """
        Validate that the receiver is a participant in the conversation if set
        """
        from django.core.exceptions import ValidationError

        if self.receiver and self.conversation:
            if self.receiver not in self.conversation.participants.all():
                raise ValidationError(
                    "Receiver must be a participant in the conversation"
                )

    def __str__(self):
        """
        returns the message timestamp, sender, and content
        """
        return f"{self.sender.username}, {self.edited}: {self.content[:20] if self.content else self.message_type}"


class MessageHistory(models.Model):
    """
    Models to store the message history
    """

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    edited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="message_edits"
    )
    old_content = models.TextField()
    edited_at = models.DateTimeField(auto_now=True)
    message_type = models.CharField(
        max_length=20,
        choices=[
            ("TEXT", "Text"),
            ("IMAGE", "Image"),
            ("FILE", "File"),
        ],
        default="TEXT",
    )

    def __str__(self):
        return f"{self.editor.username} {self.content[:20] if self.content else self.message_type}"

    class Meta:
        ordering = ["edited_at"]


class Notification(models.Model):
    """
    Model to store notifications
    """

    # recepient
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    # triggering message
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=20, default="new_message")

    class Meta:
        ordering = ["-created_at"]
