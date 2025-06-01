#!/usr/bin/env python3
"""
viewsets
"""
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


# Create your views here.
class ConversationViewSet(viewsets.ModelViewSet):
    """
    concversation viewset
    """
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

    def create(self, request, *args, **kwargs):
        """
        creates a convesration
        """
        user_ids = request.data.get("participants", [])

        if not user_ids or len(user_ids) < 2:
            return Response({"error": "Convo must have \
                2/more participants."}, status=400)
        users = User.objects.filter(id__in=user_ids)
        if users.count() != len(user_ids):
            return Response({"error": "One or more users not found."},
                            status=400)

        conversation = Conversation.objects.create()
        conversation.participants.set(users)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    viewset for messages
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def create(self, request, *args, **kwargs):
        """
        creates messages
        """
        conversation_id = request.data.get("converation")
        sender_id = request.data.get("sender")
        content = request.data.get("content")

        if not (conversation_id and sender_id and content):
            return Response({"error": "convo sender, & content required"},
                            status=400)
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            sender = User.objects.get(id=sender_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversation not found"}, status=404)
        except User.DoesNotExist:
            return Response({"error": "Sender not found"}, status=404)

        # check if sender in conversation
        if sender not in conversation.participants.all():
            return Response({"error": "Sender not part of Conversation"},
                            status=403)
        message = Message.objects.create(conversation=conversation,
                                         sender=sender, content=content)
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
