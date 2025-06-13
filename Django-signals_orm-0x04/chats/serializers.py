#!/usr/bin/env python3
"""
The model serializers
They convert model instances
into json for the API resposnes. They also convert
JSON into model nstances when creating or udating data
"""
import re
from rest_framework import serializers
from .models import User, Message, Conversation, Notification, MessageHistory
import logging


logger = logging.getLogger(__name__)


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
    receiver = LightUserSerializer(read_only=True, allow_null=True)
    # conversation = ConversationSerializer(read_only=True)

    # to accept sender id in a post
    sender_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), write_only=True, source="sender"
    )

    # Accept receiver id in a post
    # receiver_id = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.all(), write_only=True, source="receiver", allow_null=True
    # )
    receiver_id = serializers.CharField(write_only=True, allow_null=True)

    # Accept convesation id in a post
    # conversation_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Conversation.objects.all(), write_only=True, source="conversation"
    # )
    conversation_id = serializers.CharField(write_only=True)
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
            "content",
            "timestamp",
            "edited",
            "message_type",
            "attachment",
            "read_by",
            "parent_message",
            "replies",
        ]
        read_only_fields = ["sender", "timestamp", "replies"]

    def get_replies(self, obj):
        return MessageSerializer(obj.replies.all(), many=True).data

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
        validate message type and attachment and ensure receiver is participant in conversation
        """
        if isinstance(self.initial_data, list):
            raise serializers.ValidationError(
                {
                    "non_field_errors": "Invalid data. Expected a dictionary, but got list."
                }
            )
        conversation = data.get("conversations", {}).get("conversation_id")
        receiver = data.get("receiver")
        message_type = data.get("message_type", "TEXT")
        attachment = data.get("attachment")

        if (
            receiver
            and conversation
            and receiver not in conversation.participants.all()
        ):
            raise serializers.ValidationError(
                "Receiver must be a participant in a conversation."
            )

        if message_type != "TEXT" and not attachment:
            raise serializers.ValidationError(
                f"Attachment required for {message_type} message"
            )
        return data

    # def validate(self, data):
    #     # if isinstance(self.initial_data, list):
    #     #     raise serializers.ValidationError(
    #     #         {
    #     #             "non_field_errors": "Invalid data. Expected a dictionary, but got list."
    #     #         }
    #     #     )
    #     conversation_id = data.get("conversation", {}).get("conversation_id")
    #     receiver = data.get("receiver")
    #     try:
    #         if conversation_id:
    #             conversation = Conversation.objects.get(conversation_id=conversation_id)
    #             if receiver and receiver not in conversation.participants.all():
    #                 raise serializers.ValidationError(
    #                     {
    #                         "receiver_id": "Receiver must be a participant in the conversation."
    #                     }
    #                 )
    #             if self.context["request"].user not in conversation.participants.all():
    #                 raise serializers.ValidationError(
    #                     {
    #                         "conversation_id": "You are not a participant in this conversation."
    #                     }
    #                 )
    #         else:
    #             raise serializers.ValidationError(
    #                 {"conversation_id": "This field is required."}
    #             )
    #     except Conversation.DoesNotExist:
    #         raise serializers.ValidationError(
    #             {"conversation_id": "Conversation does not exist."}
    #         )
    #     except Exception as e:
    #         logger.error(f"MessageSerializer validation error: {e}")
    #         print(f"message serializer validation error: {e}")
    #         raise
    #     return data


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


class NotificationSerializer(serializers.ModelSerializer):
    """
    serializer for Notifications model
    """

    user = UserSerializer(read_only=True)
    message = MessageSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "user", "message", "created_at", "is_read", "notification_type"]
        read_only_fields = ["created_at", "user", "message", "notification_type"]


class MessageHistorySerializer(serializers.ModelSerializer):
    """
    serializer for message history model
    """

    edited_by = LightUserSerializer(read_only=True)

    class Meta:
        model = MessageHistory
        fields = ["old_content", "edited_by", "edited_at"]
        read_only_fields = ["old_content", "edited_by", "edited_at"]
