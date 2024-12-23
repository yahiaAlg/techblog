from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, RedirectView
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import SignUpForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import Profile, EmailVerification, LoginHistory
from datetime import timedelta

class SignUpView(SuccessMessageMixin, CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')
    success_message = "Your account was created successfully. Please check your email to verify your account."

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance
        
        # Create verification token
        token = get_random_string(64)
        expires_at = timezone.now() + timedelta(days=7)
        EmailVerification.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
        
        # Send verification email
        context = {
            'user': user,
            'token': token,
            'protocol': 'https' if self.request.is_secure() else 'http',
            'domain': self.request.get_host(),
        }
        send_mail(
            subject='Verify your email address',
            message=render_to_string('accounts/emails/verify_email.txt', context),
            from_email=None,  # Use DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            html_message=render_to_string('accounts/emails/verify_email.html', context)
        )
        
        return response

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        
        # Record login history
        LoginHistory.objects.create(
            user=form.get_user(),
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
            success=True
        )
        
        return response

class CustomLogoutView(LogoutView):
    next_page = 'accounts:login'

class ProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user.profile_owner


    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile has been updated successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_history'] = self.request.user.loginhistory_set.all()[:5]
        context['articles'] = self.request.user.articles.all()[:5]  # Use 'articles'
        context['comments'] = self.request.user.comments.all()[:5]  # Use 'comments'
        return context

class PublicProfileView(DetailView):
    model = User
    template_name = 'accounts/public_profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['articles'] = user.article_set.filter(status='published')
        context['comments'] = user.comment_set.filter(is_approved=True)
        return context

class EmailVerificationView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        token = self.kwargs.get('token')
        verification = get_object_or_404(EmailVerification, token=token)
        
        if verification.is_valid():
            user = verification.user
            profile = user.profile_owner
            profile.email_verified = True
            profile.save()
            
            messages.success(self.request, 'Your email has been verified successfully.')
            return reverse_lazy('accounts:login')
        else:
            messages.error(self.request, 'This verification link has expired or is invalid.')
            return reverse_lazy('accounts:signup')

class PasswordResetRequestView(PasswordResetView):
    template_name = 'accounts/password_reset_request.html'
    email_template_name = 'accounts/emails/password_reset_email.txt'
    html_email_template_name = 'accounts/emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Password reset instructions have been sent to your email.')
        return response

class PasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your password has been reset successfully.')
        return response

class AccountSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.request.user.profile_owner
        context['login_history'] = self.request.user.loginhistory_set.all()[:10]
        return context