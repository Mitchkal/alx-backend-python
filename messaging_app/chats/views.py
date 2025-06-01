#!/usr/bin/env python3
"""
viewsets
"""
from django.shortcuts import render
from django_filters_rest_framework import DjangoFilterBackend
from .filters import ConversationFilter, MessageFilter
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your views here.
class ConversationViewSet(viewsets.ModelViewSet):
    """
    viewset for managing conversation
    """

    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ConversationFilter

    def get_queryset(self):
        """
        Filter conversations to include only where
        requesting user is participant
        """
        return self.queryset.filter(participants=self.request.user).prefetch_related(
            "participants", "messages"
        )

    def create(self, request, *args, **kwargs):
        """
        creates a convesration
        request: HTTP request with participant IDS in the 'participants
        field
        Returns a serialized conversation with HTTP 201 status on success
        or error message with HTTP 400 status for failure
        """
        user_ids = request.data.get("participants", [])

        if not user_ids or len(user_ids) < 2:
            return Response(
                {"error": "Conversation must have 2/more participants."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.id not in user_ids:
            return Response(
                {"error": "Requesting user must be a participant."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        users = User.objects.filter(id__in=user_ids)
        if users.count() != len(user_ids):
            return Response(
                {"error": "One or more users not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        conversation = Conversation.objects.create()
        conversation.participants.set(users)
        serializer = self.get_serializer(conversation, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    viewset for managing messages
    """

    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        """
        Filter messages to include only thise where user is participant
        """
        return self.queryset.filter(
            conversation__participats=self.request.user
        ).select_related("sender", "conversation")

    def create(self, request, *args, **kwargs):
        """
        creates a new message in a conversation
        request: contains message data
        Returns a serialized message object with HTTP 201 status for success
        or error message with HTTP 403/400 status on failure
        """
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        conversation = serializer.validated_data["conversation"]
        sender = serializer.validated_data["sender"]

        if sender not in conversation.participants.all():
            return Response(
                {"error": "Sender not participant in this conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
