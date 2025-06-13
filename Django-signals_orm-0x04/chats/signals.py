from .models import Message, Notification
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import logging

# logger = logging.get(__name__)


@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    """
    creates a notification for recepients when new message is created
    """
    if created:
        # for direct messages notify receiver if set
        if instance.receiver:
            # if sender.receiver:
            try:
                Notification.objects.create(
                    user=instance.receiver,
                    message=instance,
                    notification_type="new_message",
                )
            except Exception as e:
                # log error to avoid test fail
                logger = logging.getLogger(__name__)
                logger.Error(
                    f"Failed to create notification for receiver {instance.receiver}: {e}"
                )
        else:
            # for group messages notify all group participants except sender
            try:
                recipients = instance.conversation.participants.exclude(
                    user_id=instance.sender_id
                )
                if recipients.exists():
                    for user in recipients:
                        Notification.objects.create(
                            user=user, message=instance, notification_type="new_message"
                        )
            except Exception as e:
                logger.error(
                    f"Failed to create group notifications for message {instance.message_id}: {e}"
                )


# @receiver(pre_save, sender=Message)
# def log_message_edit(sender, **kwargs):
#     # pass
#     if sender.pk is None:
#         message = sender.objects.get
#     return
