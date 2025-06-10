#!/usr/bin/env python3
"""
custom permisision class for chat app
"""
from rest_framework import permissions
from .models import Conversation, Message


class IsParticipantOfConversation(permissions.BasePermission):
    """
    permission class for only authenticated uses to
    access api, only participants in  conversation
    to send, view, update or delete messages
    """

    def has_permission(self, request, view):
        """
        ensure user authentication for all actions
        """
        if not request.user.is_authenticated:
            return False

        # When creating a message, check if a user is a participanty in
        #  the specified conversation
        if view.action == "create" and request.data.get("conversation"):
            try:
                conversation_id = request.data.get("conversation")
                conversation = Conversation.objects.get(conversation_id=conversation_id)
                return request.user in conversation.participants.all()
            except Conversation.DoesNotExist:
                return False
        # for other actions, rely on object-level permissions
        # or allow authenticated users
        return True

    def has_object_permission(self, request, view, obj):
        """
        handle conversation objects. Checks if a user is aparticipant
        in a given conversation for the given object. For messages,
        restrict GET, PUT, PATCH, DELETE to conversation participant.
        For conversations, restrict to participants.

        """

        # Allow superuser full access
        if request.user.is_superuser:
            return True

        if isinstance(obj, Conversation):
            # for conversation objects
            return request.user in obj.participants.all()

        if isinstance(obj, Message):
            # for message objects Allow GET, PUT, PATCH,
            # DELETE only for conversation
            # participants
            if request.method in ["GET", "PUT", "PATCH", "DELETE"]:
                return request.user in obj.conversation.participants.all()
        return False
