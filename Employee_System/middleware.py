from django.utils import timezone

class UpdateLastSeenMiddleware:
    """
    Middleware to update the last_seen field for a logged-in user on each request.
    This helps to track a user's activity and determine their online status.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # We only want to update the timestamp if a user is authenticated
        if request.user.is_authenticated:
            # We also check that the user has a last_seen attribute
            # to avoid errors with other user models
            if hasattr(request.user, 'last_seen'):
                request.user.last_seen = timezone.now()
                request.user.save()

        response = self.get_response(request)
        return response
