from django.utils import timezone

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process the request
        response = self.get_response(request)

        # Update last_activity for authenticated users
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.last_activity = timezone.now()
            profile.save(update_fields=['last_activity'])

        return response 