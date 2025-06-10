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

    password = serializers.CharField(min_length=8, write_only=True)

    class Meta:
        """
        meta class
        """

        model = User
        fields = [
            "user_id",
            "email",
            "first_name",
            "username",
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
        fields = ["user_id", "email"]


class MessageSerializer(serializers.ModelSerializer):
    """
    The message serializer
    """

    # facilitates nested relationship where message shows sender info
    # and not just a sender id
    sender = LightUserSerializer(read_only=True)
    receiver = LightUserSerializer(read_only=True)

    # to accept sender id in a post
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="sender"
    )

    # Accept receiver id in a post
    receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="receiver"
    )

    # Accept convesation id in a post
    conversation_id = serializers.PrimaryKeyRelatedField(
        queryset=Conversation.objects.all(), write_only=True, source="conversation"
    )
    # read by attribute for messages in a conversation
    read_by = LightUserSerializer(many=True, read_only=True)

    class Meta:
        """
        meta class
        """

        model = Message
        fields = [
            "message_id",
            "sender",  # nested read
            "sender_id",  # write only
            "receiver",  # nested read
            "receiver_id",  # write only
            "conversation_id",  # write only
            "message_body",
            "sent_at",
            "message_type",
            "attachment",
            "read_by",
        ]

    def create(self, validated_data):
        """
        create new message with provider sender and conversation
        """
        try:
            message = Message.objects.create(**validated_data)
            # mark message as read by sender
            message.read_by.add(validated_data["sender"])
            return message
        except Exception as e:
            raise serializers.ValidationError(f"Failed to create message: {str(e)}")

    def validate(self, data):
        """
        validate message type and attachment
        """
        message_type = data.get("message_type", "TEXT")
        attachment = data.get("attachment")
        if message_type != "TEXT" and not attachment:
            raise serializers.ValidationError(
                f"Attachment required for {message_type} message"
            )
        return data


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
        child=serializers.UUIDField(), write_only=True
    )
    last_message = serializers.SerializerMethodField()

    class Meta:
        """
        meta class
        """

        model = Conversation
        fields = [
            "conversation_id",
            "participants",
            "participant_ids",
            "name",
            "created_at",
            "messages",
            "last_message",
        ]

    def get_last_message(self, obj):
        """
        get most recent message in conversation
        """
        last_message = obj.last_message()
        return MessageSerializer(last_message).data if last_message else None

    def create(self, validated_data):
        """
        Create new conversation with participants
        """
        try:
            participant_ids = validated_data.pop("participant_ids")
            users = User.objects.filter(user_id__in=participant_ids)
            if users.count() != len(participant_ids):
                raise serializers.ValidationError("One or more users not found")
            conversation = Conversation.objects.create(**validated_data)
            conversation.participants.set(users)
            return conversation
        except Exception as e:
            raise serializers.ValidationError(
                f"Failed to create conversation: {str(e)}"
            )
