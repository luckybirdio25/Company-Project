from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, Role

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Get or create the default role with no permissions
        default_role, _ = Role.objects.get_or_create(
            name='User',
            defaults={
                'description': 'Default user role with no permissions',
                'permissions': {}
            }
        )
        UserProfile.objects.create(user=instance, role=default_role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        create_user_profile(sender, instance, True, **kwargs)
    else:
        instance.profile.save() 