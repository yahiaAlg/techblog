from rest_framework.throttling import BaseThrottle
from django.core.cache import cache
from django.utils import timezone

class APIKeyThrottle(BaseThrottle):
    def get_cache_key(self, request, view):
        if not request.auth:
            return None
        return f'throttle_api_key_{request.auth.key}'

    def allow_request(self, request, view):
        if not request.auth:
            return False

        now = timezone.now()
        cache_key = self.get_cache_key(request, view)
        
        # Get rate limits
        rate_limit = request.auth.rate_limit
        if not rate_limit:
            return False

        # Get current counts from cache
        history = cache.get(cache_key, {
            'minute': {'count': 0, 'reset': now},
            'hour': {'count': 0, 'reset': now},
            'day': {'count': 0, 'reset': now}
        })

        # Reset counters if time windows have passed
        if (now - history['minute']['reset']).total_seconds() > 60:
            history['minute'] = {'count': 0, 'reset': now}
        if (now - history['hour']['reset']).total_seconds() > 3600:
            history['hour'] = {'count': 0, 'reset': now}
        if (now - history['day']['reset']).total_seconds() > 86400:
            history['day'] = {'count': 0, 'reset': now}

        # Check limits
        if (history['minute']['count'] >= rate_limit.requests_per_minute or
            history['hour']['count'] >= rate_limit.requests_per_hour or
            history['day']['count'] >= rate_limit.requests_per_day):
            return False

        # Increment counters
        history['minute']['count'] += 1
        history['hour']['count'] += 1
        history['day']['count'] += 1

        # Update cache
        cache.set(cache_key, history, 86400)

        return True

    def wait(self):
        return 60