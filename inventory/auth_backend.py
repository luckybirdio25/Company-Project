from django.contrib.auth.backends import ModelBackend
from django.utils import timezone

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        if user is not None:
            # Update last_login and last_activity in profile
            if hasattr(user, 'profile'):
                profile = user.profile
                profile.last_login = timezone.now()
                profile.last_activity = timezone.now()
                profile.save(update_fields=['last_login', 'last_activity'])
        return user 