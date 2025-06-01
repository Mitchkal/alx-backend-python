#!/usr/bin/env python3
"""
The model serializers
They convert model instances
into json for the API resposnes. They also convert
JSON into model nstances when creating or udating data
"""
from rest_framework import serializers
from .models import User, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """
    serializer for users
    """

    class Meta:
        """
        meta class
        """

        model = User
        fields = ["id", "username", "bio", "email", "profile_picture"]


class MessageSerializer(serializers.ModelSerializer):
    """
    The message serializer
    """

    # facilitates nested relationship where message shows sender info
    # and not just a sender id
    sender = UserSerializer(read_only=True)

    class Meta:
        """
        meta class
        """

        model = Message
        field = ["id", "sender", "content", "timestamp"]


class ConversationSerializer(serializers.ModelSerializer):
    """
    The conversation serializer
    Serialize both the participants as the users
    and the messages nested inside
    """

    # Show all users in a conversation
    participants = UserSerializer(many=True, read_only=True)
    # Show all related messages
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        """
        meta class
        """

        model = Conversation
        fields = ["id", "participants", "created_at", "messages"]
