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
        return True

    def has_object_permission(self, request, view, obj):
        """
        handle conversation objects
        """
        if isinstance(obj, Conversation):
            # for conversation objects
            return request.user in obj.participants.all()

        if isinstance(obj, Message):
            # for message objects
            return request.user in obj.conversation.participants.all()
        return False
