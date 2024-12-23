from rest_framework.throttling import BaseThrottle
from django.core.cache import cache
from django.utils import timezone
import time


class APIKeyThrottle(BaseThrottle):
    def get_cache_key(self, request, view):
        if not request.auth:
            return None
        return f"throttle_api_key_{request.auth.key}"

    def allow_request(self, request, view):
        if not request.auth:
            return False

        api_key = request.auth
        rate_limit = api_key.rate_limit

        now = timezone.now()
        cache_key = self.get_cache_key(request, view)

        # Get current counts from cache
        counts = cache.get(
            cache_key,
            {
                "minute": {"count": 0, "reset": now},
                "hour": {"count": 0, "reset": now},
                "day": {"count": 0, "reset": now},
            },
        )

        # Reset counters if time windows have passed
        minute_ago = now - timezone.timedelta(minutes=1)
        hour_ago = now - timezone.timedelta(hours=1)
        day_ago = now - timezone.timedelta(days=1)

        if counts["minute"]["reset"] < minute_ago:
            counts["minute"] = {"count": 0, "reset": now}
        if counts["hour"]["reset"] < hour_ago:
            counts["hour"] = {"count": 0, "reset": now}
        if counts["day"]["reset"] < day_ago:
            counts["day"] = {"count": 0, "reset": now}

        # Check limits
        if (
            counts["minute"]["count"] >= rate_limit.requests_per_minute
            or counts["hour"]["count"] >= rate_limit.requests_per_hour
            or counts["day"]["count"] >= rate_limit.requests_per_day
        ):
            return False

        # Increment counters
        counts["minute"]["count"] += 1
        counts["hour"]["count"] += 1
        counts["day"]["count"] += 1

        # Update cache
        cache.set(cache_key, counts, 86400)  # Cache for 24 hours

        return True

    def wait(self):
        """
        Returns the recommended next request time in seconds.
        """
        return 60
