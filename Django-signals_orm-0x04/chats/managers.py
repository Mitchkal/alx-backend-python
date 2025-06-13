from django.db import models


class MessageManager(models.Manager):
    """
    Manager model for unread messagea
    """

    def unread_for_user(self, user):
        return (
            self.get_queryset()
            .exclude(read_by=user)
            .filter(receiver=user)  # filter messages meant for only this user
            .only("message_id", "content", "timestamp", "sender", "conversation")
        )
