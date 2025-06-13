from .models import Message, Notification, MessageHistory
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
import logging
from datetime import timezone
from django.contrib.auth import get_user_model

User = get_user_model()
logger = logging.getLogger(__name__)


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
                print(
                    f"Failed to create notification for receiver {instance.receiver}: {e}"
                )
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
                print(
                    f"Failed to create group notifications for message {instance.message_id}: {e}"
                )
                logger.error(
                    f"Failed to create group notifications for message {instance.message_id}: {e}"
                )


@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    # pass
    if instance.pk:
        try:
            old_instance = Message.objects.get(pk=instance.pk)
            if old_instance.content != instance.content:
                logger.info(f"Message{instance.message_id} edited by {instance.sender}")
                print(f"Message{instance.message_id} edited by {instance.sender}")
                MessageHistory.objects.create(
                    message=instance,
                    old_content=old_instance.content,
                    edited_by=instance.sender,
                )
                instance.edited = True
                instance.edited_at = timezone.now()

        except Message.DoesNotExist:
            logger.warning(f"Message {instance.message_id} not found for edit logging")
            print(f"Message {instance.message_id} not found for edit logging")
        except Exception as e:
            logger.error(f"Error logging edit for message {instance.message_id}: {e}")
            print(f"Error logging edit for message {instance.message_id}: {e}")


@receiver(post_delete, sender=User)
def delete_related_user_data(sender, instance, **kwargs):
    """
    cleans up data for deletes user
    """
    print(f"Cleaning up data for deleted user: {instance.username}")
    # delete messages
    Message.objects.filter(sender=instance).delete()
    # Delete Notifications
    Notification.objects.filter(user=instance).delete()
    # Delete message history
    MessageHistory.objects.filter(edited_by=instance).delete()
