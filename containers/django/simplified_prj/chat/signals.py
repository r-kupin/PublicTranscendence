from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from models import Message


# @receiver(post_delete, sender=Message)
# def refresh_on_new_message(sender, instance, **kwargs):
#