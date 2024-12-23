from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from .models import APIKey

class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY') or request.query_params.get('api_key')
        
        if not api_key:
            return None

        try:
            key = APIKey.objects.get(key=api_key, is_active=True)
            
            # Update last used timestamp
            key.last_used_at = timezone.now()
            key.save()
            
            return (key.user, key)
        except APIKey.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')