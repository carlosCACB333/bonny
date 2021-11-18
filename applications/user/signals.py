from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import Person


# @receiver(pre_delete, sender=Person)
# def delete_picture(sender, **kwargs):
#     print("----------------", sender)
