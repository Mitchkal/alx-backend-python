#!/usr/bin/env python3
"""
models file
"""
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    user model
    """

    user_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    status = models.CharField(max_length=100, default="Hey there! Im using ChatApp")
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

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
        return self.username


class Conversation(models.Model):
    """
    conversations model
    """

    conversation_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False
    )

    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """
        return participant names in a conversation
        """
        participants = self.participants.values_list('username', flat=True)
        participant_names = ", ".join(participants)
        return f"Conversation between {participant_names}"


class Message(models.Model):
    """
    model for the chat messages
    """

    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        returns the message timestamp, sender, and content
        """
        return f"{self.sender.username}: {self.message_body[:20]}"
