#!/usr/bin/env python3
"""
models file
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    user model
    """

    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profiles/", blank=True, null=True)
    date_of_join = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField()

    def __str__(self):
        """
        return user name
        """
        return self.username


class Conversation(models.Model):
    """
    conversations model
    """

    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        return participant names in a conversation
        """
        participant_names = ", ".join(
            [user.username for user in self.participants.all()]
        )
        return f"Conversation between {participant_names}"


class Message(models.Model):
    """
    model for the chat messages
    """

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        returns the message timestamp, sender, and content
        """
        return f"{self.sender.username}: {self.content[:20]}"
