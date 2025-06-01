#!/usr/bin/env python3
"""
The model serializers
They convert model instances
into json for the API resposnes. They also convert
JSON into model nstances when creating or udating data
"""
import re
from rest_framework import serializers
from .models import User, Message, Conversation


class UserSerializer(serializers.ModelSerializer):
    """
    serializer for users
    """

    password = serializers.CharField(min_length=8)

    class Meta:
        """
        meta class
        """

        model = User
        fields = [
            "user_id",
            "username",
            "first_name",
            "last_name",
            "profile_picture",
            "status",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        """
        creates new user with hashed password
        """
        try:
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create user: {str(e)}")

    def validate_password(self, value):
        """
        Validates passsword meets security requirements
        """
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError(
                "Password must contain at least one special character"
            )
        return value


class LightUserSerializer(serializers.ModelSerializer):
    """
    light serializer for sender
    """

    class Meta:
        """
        meta class
        """

        model = User
        fields = ["id", "username"]


class MessageSerializer(serializers.ModelSerializer):
    """
    The message serializer
    """

    # facilitates nested relationship where message shows sender info
    # and not just a sender id
    sender = LightUserSerializer(read_only=True)

    # to accept sender id in a post
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True
    )

    # Accept convesation id in a post
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(), write_only=True
    )

    class Meta:
        """
        meta class
        """

        model = Message
        fields = [
            "message_id",
            "sender",  # nested read
            "sender_id",  # write only
            "conversation_id",  # write only
            "message_body",
            "sent_at",
        ]

    def create(self, validated_data):
        """
        create new message with provider sender and conversation
        """
        try:
            sender = validated_data.pop("sender_id")
            conversation = validated_data.pop("conversation_id")

            # create message with foreign keys
            return Message.objects.create(
                sender=sender, conversation=conversation, **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create message: {str(e)}")


class ConversationSerializer(serializers.ModelSerializer):
    """
    The conversation serializer
    Handle conversation creation and retrieval
    """

    # Show all users in a conversation
    participants = LightUserSerializer(many=True, read_only=True)
    # Show all related messages
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        """
        meta class
        """

        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "created_at",
            "messages",
        ]
