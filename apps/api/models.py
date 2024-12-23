# Create your models here.
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class APIKey(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="api_keys"
    )
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("API Key")
        verbose_name_plural = _("API Keys")

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class APIRequest(models.Model):
    api_key = models.ForeignKey(
        APIKey, on_delete=models.CASCADE, related_name="requests"
    )
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()
    response_time = models.FloatField()  # in milliseconds
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)

    class Meta:
        verbose_name = _("API Request")
        verbose_name_plural = _("API Requests")
        ordering = ["-timestamp"]


class APIRateLimit(models.Model):
    api_key = models.OneToOneField(
        APIKey, on_delete=models.CASCADE, related_name="rate_limit"
    )
    requests_per_minute = models.PositiveIntegerField(default=60)
    requests_per_hour = models.PositiveIntegerField(default=1000)
    requests_per_day = models.PositiveIntegerField(default=10000)

    class Meta:
        verbose_name = _("API Rate Limit")
        verbose_name_plural = _("API Rate Limits")
