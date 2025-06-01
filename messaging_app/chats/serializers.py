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

    password = serializers.CharField(write_only=True, min_length=8)

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
        creates validated data
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_password(self, value):
        """
        custom password validation
        """
        if "password" in value.lower():
            raise serializers.ValidationError(
                "Password should not contain the word 'password'."
            )
        return value


class MessageSerializer(serializers.ModelSerializer):
    """
    The message serializer
    """

    # facilitates nested relationship where message shows sender info
    # and not just a sender id
    sender = UserSerializer(read_only=True)

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
        Extract write-only fields and remove from data
        """
        sender = validated_data.pop("sender_id")
        conversation = validated_data.pop("conversation_id")

        # create message with foreign keys
        return Message.objects.create(
            sender=sender, conversation=conversation, **validated_data
        )


class ConversationSerializer(serializers.ModelSerializer):
    """
    The conversation serializer
    Serialize both the participants as the users
    and the messages nested inside
    """

    # Show all users in a conversation
    participants = UserSerializer(many=True, read_only=True)
    # Show all related messages
    messages = serializers.SerializerMethodField()  # include nested message
    # messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        """
        meta class
        """

        model = Conversation
        fields = ["conversation_id", "participants", "created_at", "messages"]

    def get_messages(self, obj):
        """
        get all messages for a conversation
        """
        messages = Message.objects.filter(conversation=obj)
        return MessageSerializer(messages, many=True).data
