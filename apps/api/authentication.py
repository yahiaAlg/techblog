from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import CustomUser


class APIKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class that authenticates users based on an API key.
    """

    def authenticate(self, request):
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            return None  # No authentication attempted

        try:
            user = CustomUser.objects.get(
                loginhistory__token=api_key, email_verified=True
            )
            if not api_key:
                raise CustomUser.objects()
        except (CustomUser.DoesNotExist, AttributeError):
            raise AuthenticationFailed(_("Invalid API key or no matching user found."))

        return (user, None)
