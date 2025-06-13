#!/usr/bin/env python3
"""
viewsets
"""
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ConversationFilter, MessageFilter, UserFilter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import HttpResponse
from .models import Conversation, Message, User, Notification
from .serializers import (
    ConversationSerializer,
    MessageSerializer,
    UserSerializer,
    NotificationSerializer,
)
from .permissions import IsParticipantOfConversation
from django.db.models import F, OuterRef, Subquery
from .pagination import MessagePagination


class UserViewSet(viewsets.ModelViewSet):
    """
    viewset to view users
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        """
        Filter messages to include only thise where user is participant
        pre-fetches sender and conversation
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                return User.objects.all()

            shared_conversations = (
                self.queryset.filter(conversation__participants=user)
                .select_related("sender", "conversation")
                .prefetch_related("read_by")
            )
            return User.objects.filter(
                conversations__in=shared_conversations
            ).distinct()
        return User.objects.none()


# Create your views here.
class ConversationViewSet(viewsets.ModelViewSet):
    """
    viewset for managing conversation
    """

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        """
        Filter conversations to include only where
        requesting user is participant
        """
        user = self.request.user
        if user.is_authenticated:
            # obtain sent at of last message
            latest_message = (
                Message.objects.filter(conversation=OuterRef("conversation_id"))
                .order_by("-timestamp")
                .values("timestamp")[:1]
            )
            return (
                Conversation.objects.all()
                .filter(participants=user)
                .annotate(latest_message_time=Subquery(latest_message))
                .prefetch_related("participants", "messages")
                .order_by(F("latest_message_time").desc(nulls_last=True))
            )
        return Conversation.objects.none()

    def perform_create(self, serializer):
        """
        create conversation and add authenticated user as participant
        """
        conversation = serializer.save()
        conversation.participants.add(self.request.user)
        user_ids = self.request.data.get("participant_ids", [])
        if user_ids:
            users = User.objects.filter(user_id_in=user_ids)
            conversation.participants.add(*users)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """
        Retrieve all messsages in conversation
        """
        conversation = self.get_object()
        messages = Message.objects.filter(conversation=conversation)
        paginator = MessagePagination()
        page = paginator.paginate_queryset(messages, request)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageViewSet(viewsets.ModelViewSet):
    """
    viewset for managing messages
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    # permission_classes = [IsAuthenticated, IsConversationParticipant]
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        """
        Filter messages to include only thise where user is participant
        pre-fetches sender and conversation
        """
        user = self.request.user
        if user.is_authenticated:
            return (
                self.queryset.filter(conversation__participants=user)
                .select_related("sender", "conversation")
                .prefetch_related("read_by")
            )
        return Message.objects.none()

    def get_permissions(self):
        """
        gets participant permissions
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsParticipantOfConversation()]
        return [IsParticipantOfConversation()]

    def perform_create(self, serializer):
        """
        creates a message and update the conversation's last
        message sets sender to requesting user
        self.request: contains message data(conversation, message_body,
        message_type, optional attachment)
        Returns a serialized message object with HTTP 201 status for success
        or error message with HTTP 403/400 status on failure
        alternatively:
               message = serializer.save(sender=self.request.user)
                message.read_by.add(self.request.user)

        """
        message = serializer.save(sender=self.request.user)
        message.read_by.add(self.request.user)
        message.conversation.last_message = message
        message.conversation.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related(
            "user", "message"
        )

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({"status": "notification marked as read"})


def root_view(request):
    return HttpResponse("Welcome to the Messaging App")
