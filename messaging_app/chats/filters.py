# chats/filters.py
from django_filters import rest_framework as filters
from .models import Conversation, Message


class ConversationFilter(filters.FilterSet):
    participant = filters.NumberFilter(field_name="participants__id")
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Conversation
        fields = ["participant", "created_at"]


class MessageFilter(filters.FilterSet):
    sender = filters.NumberFilter(field_name="sender__id")
    conversation = filters.NumberFilter(field_name="conversation__id")
    sent_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_at"]
