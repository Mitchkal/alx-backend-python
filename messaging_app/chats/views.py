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
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer, UserSerializer
from .permissions import IsParticipantOfConversation
from django.db.models import F, OuterRef, Subquery

# from django.contrib.auth import get_user_model
# from django.db.models import Count


# User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    viewset to view users
    """

    serualizer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter

    def get_queryset(self):
        """
        optionally restrics returned users toa  given email by
        filtering againsta an email query param in the url
        """
        queryset = User.objects.all()
        email = self.request.query_params.get("email", None)
        if email is not None:
            queryset = queryset.filter(email__iexact=email)
        return queryset


# class IsConversationParticipant(BasePermission):
#     """
#     Custom permission to ensure user is a participant in the conversation
#     """

#     def has_object_permission(self, request, view, obj):
#         if isinstance(obj, Message):
#             return obj.conversation.participants.filter(
#                 user_id=request.user.user_id
#             ).exists()
#         return obj.participants.filter(user_id=request.user.user_id).exists()


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
                Message.objects.filter(conversation=OuterRef("pk"))
                .order_by("-sent_at")
                .values("sent_at")[:1]
            )
            return (
                Conversation.objects.all()
                .filter(participants=user)
                .annotate(latest_message_time=Subquery(latest_message))
                .prefetch_related("participants", "messages")
                .order_by(F("latest_message_time").desc(nulls_last=True))
            )
        return Conversation.objects.none()
        # return self.queryset.filter(participants=self.request.user).prefetch_related(
        #     "participants", "messages"
        # )

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
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    # def create(self, request, *args, **kwargs):
    #     """
    #     creates a convesration
    #     request: HTTP request with participant IDS in the 'participants
    #     field
    #     Returns a serialized conversation with HTTP 201 status on success
    #     or error message with HTTP 400 status for failure
    #     """

    #     serializer = self.get_serializer(
    #         data=request.data, context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     try:
    #         conversation = serializer.save()
    #         print("saved conversation", conversation)
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     except ValueError as e:  # Handle duplicate conversation error from model
    #         existing = (
    #             Conversation.objects.filter(
    #                 participants__user_id__in=serializer.validated_data[
    #                     "participant_ids"
    #                 ]
    #             )
    #             .annotate(num_participants=Count("participants"))
    #             .filter(num_participants=2)
    #             .first()
    #         )
    #         if existing:
    #             serializer = self.get_serializer(existing, context={"request": request})
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         raise serializer.ValidationError(str(e))


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

    def perform_create(self, serializer):
        """
        creates a message and update the conversation's last
        message sets sender to requesting user
        self.request: contains message data(conversation, message_body,
        message_type, optional attachment)
        Returns a serialized message object with HTTP 201 status for success
        or error message with HTTP 403/400 status on failure

        """
        message = serializer.save(sender=self.request.user)
        message.read_by.add(self.request.user)
        message.conversation.last_message = message
        message.conversation.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def create(self, request, *args, **kwargs):
    #     """
    #     creates a new message in a conversation
    #     request: contains message data(conversation, message_body,
    #     message_type, optional attachment)
    #     Automatically sets sender to requesting user
    #     Returns a serialized message object with HTTP 201 status for success
    #     or error message with HTTP 403/400 status on failure
    #     """
    #     serializer = self.get_serializer(
    #         data=request.data, context={"request": request}
    #     )
    #     serializer.is_valid(raise_exception=True)

    #     # Ensure sender is the requesting user
    #     if serializer.validated_data["sender"] != request.user:
    #         return Response(
    #             {"error": "Sender must be the requesting user."},
    #             status=status.HTTP_403_FORBIDDEN,
    #         )

    #     message = serializer.save()
    #     print("saved message", message)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
