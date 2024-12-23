from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text=_('Required. Enter a valid email address.'))
    terms_accepted = forms.BooleanField(
        required=True,
        label=_('I accept the Terms of Service and Privacy Policy')
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_("This email address is already in use."))
        return email

class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, initial=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'location', 'birth_date', 'website', 
                 'github', 'twitter', 'linkedin', 'newsletter_subscription']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.owner:
            self.fields['first_name'].initial = self.instance.owner.first_name
            self.fields['last_name'].initial = self.instance.owner.last_name
            self.fields['email'].initial = self.instance.owner.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            owner = profile.owner
            owner.first_name = self.cleaned_data['first_name']
            owner.last_name = self.cleaned_data['last_name']
            owner.email = self.cleaned_data['email']
            owner.save()
            profile.save()
        return profile