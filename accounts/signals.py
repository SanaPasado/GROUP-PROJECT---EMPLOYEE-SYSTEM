# accounts/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Employee # Assuming your custom user model is Employee

@receiver(user_logged_in)
def set_online(sender, user, request, **kwargs):
    user.is_online = True
    user.save()

@receiver(user_logged_out)
def set_offline(sender, user, request, **kwargs):
    # This is a bit tricky, because user can be None.
    if user and user.is_authenticated:
        user.is_online = False
        user.save()