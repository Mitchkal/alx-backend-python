# chats/filters.py
from django_filters import rest_framework as filters
from .models import Conversation, Message, User
from django.db.models import Q


class ConversationFilter(filters.FilterSet):
    """
    filterset for conversations
    """

    participant = filters.NumberFilter(field_name="participants__user_id")
    created_at = filters.DateTimeFromToRangeFilter()

    class Meta:
        model = Conversation
        fields = {
            "name": ["exact", "icontains"],
            "created_at": ["exact", "gte", "lte"],
        }


class MessageFilter(filters.FilterSet):
    """
    filterset for messages
    """

    sender = filters.UUIDFilter(field_name="sender__user_id")
    conversation = filters.UUIDFilter(field_name="conversation__conversation_id")
    sent_at = filters.DateTimeFromToRangeFilter()
    message_type = filters.ChoiceFilter(
        choices=Message._meta.get_field("message_type").choices
    )

    class Meta:
        model = Message
        fields = ["sender", "conversation", "sent_at", "message_type"]


class UserFilter(filters.FilterSet):
    """
    filterset for users
    """

    email = filters.CharFilter(lookup_expr="iexact")
    username = filters.CharFilter(lookup_expr="iexact")
    first_name = filters.CharFilter(lookup_expr="icontains")
    last_name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = User
        fields = ["email", "username", "first_name", "last_name"]
