from django.utils import timezone

class UpdateLastSeenMiddleware:
    """
    Middleware to update the `last_seen` timestamp for authenticated users
    on each request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update the last_seen time for the user's profile.
            # Using update() is more efficient than get() and save() as it avoids signals.
            from inventory.models import UserProfile
            UserProfile.objects.filter(user=request.user).update(last_seen=timezone.now())
        
        response = self.get_response(request)
        return response 