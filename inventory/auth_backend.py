from django.contrib.auth.backends import ModelBackend
from django.utils import timezone

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        return user 