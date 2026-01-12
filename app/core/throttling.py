from rest_framework.throttling import UserRateThrottle


class RecipeCreateThrottle(UserRateThrottle):
    """
    Throttle for recipe creation.
    Limits authenticated users to 20 recipe creations per day.
    """
    scope = 'recipe_create'

    def allow_request(self, request, view):
        """Only throttle POST requests (recipe creation)."""
        if request.method != 'POST':
            return True
        return super().allow_request(request, view)


class BurstRateThrottle(UserRateThrottle):
    """
    Throttle for burst protection.
    Prevents rapid-fire requests from authenticated users.
    """
    scope = 'burst'
    rate = '60/minute'


class SustainedRateThrottle(UserRateThrottle):
    """
    Throttle for sustained rate limiting.
    Standard rate limit for authenticated users.
    """
    scope = 'user'
