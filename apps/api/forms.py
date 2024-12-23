from django import forms
from .models import APIKey, APIRateLimit


class APIKeyForm(forms.ModelForm):
    class Meta:
        model = APIKey
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": ("Enter a name for this API key",),
                }
            )
        }


class APIKeyRegenerationForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
        label=("I understand that the old API key will be invalidated",),
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )


class RateLimitForm(forms.ModelForm):
    class Meta:
        model = APIRateLimit
        fields = ["requests_per_minute", "requests_per_hour", "requests_per_day"]
        widgets = {
            "requests_per_minute": forms.NumberInput(attrs={"class": "form-control"}),
            "requests_per_hour": forms.NumberInput(attrs={"class": "form-control"}),
            "requests_per_day": forms.NumberInput(attrs={"class": "form-control"}),
        }
