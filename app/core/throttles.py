from rest_framework.throttling import AnonRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Throttle for authentication endpoints with stricter limits."""

    scope = "auth"
