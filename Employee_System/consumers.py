from django.utils import timezone

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if the user is authenticated and has an associated employee object
        if request.user.is_authenticated and hasattr(request.user, 'employee'):
            employee = request.user.employee
            employee.last_seen = timezone.now()
            employee.save(update_fields=['last_seen'])

        return response
