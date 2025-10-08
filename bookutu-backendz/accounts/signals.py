from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import PassengerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_passenger_profile(sender, instance, created, **kwargs):
    """
    Automatically create a PassengerProfile when a passenger user is created
    """
    if created and instance.user_type == 'PASSENGER':
        PassengerProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_passenger_profile(sender, instance, **kwargs):
    """
    Save the passenger profile when the user is saved
    """
    if instance.user_type == 'PASSENGER' and hasattr(instance, 'passenger_profile'):
        instance.passenger_profile.save()
