from django.shortcuts import render

# Create your views here.
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .forms import (
    CustomUserCreationForm,
    CustomAuthenticationForm,
    UserProfileForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
    EmailVerificationRequestForm,
)
from .models import LoginHistory, EmailVerification, PasswordReset
from datetime import timedelta

User = get_user_model()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:email_verification")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.instance

        # Create email verification token
        token = get_random_string(64)
        expires_at = timezone.now() + timedelta(days=7)
        EmailVerification.objects.create(user=user, token=token, expires_at=expires_at)

        # Send verification email
        context = {
            "user": user,
            "token": token,
            "site_name": "TechBlog",
            "protocol": "https" if self.request.is_secure() else "http",
            "domain": self.request.get_host(),
        }
        send_mail(
            subject="Verify your email address",
            message=render_to_string("accounts/emails/verify_email.txt", context),
            from_email=None,  # Use DEFAULT_FROM_EMAIL from settings
            recipient_list=[user.email],
            html_message=render_to_string("accounts/emails/verify_email.html", context),
        )

        login(self.request, user)
        messages.success(
            self.request,
            "Account created successfully. Please verify your email address.",
        )
        return response


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.get_user()

        # Update user login stats
        user.login_count += 1
        user.last_login_ip = self.request.META.get("REMOTE_ADDR")
        user.save()

        # Record login history
        LoginHistory.objects.create(
            user=user,
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )

        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)

        return response


class CustomLogoutView(LogoutView):
    next_page = "accounts:login"


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Profile updated successfully.")
        return response


class PublicProfileView(DetailView):
    model = User
    template_name = "accounts/public_profile.html"
    context_object_name = "profile_user"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context["recent_articles"] = user.articles.filter(status="published").order_by(
            "-created_at"
        )[:5]
        context["recent_comments"] = user.comments.filter(is_approved=True).order_by(
            "-created_at"
        )[:5]
        return context


class PasswordResetRequestView(TemplateView):
    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class()
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.get(email=email)

            # Create password reset token
            token = get_random_string(64)
            expires_at = timezone.now() + timedelta(hours=24)
            PasswordReset.objects.create(user=user, token=token, expires_at=expires_at)

            # Send reset email
            context = {
                "user": user,
                "token": token,
                "site_name": "TechBlog",
                "protocol": "https" if request.is_secure() else "http",
                "domain": request.get_host(),
            }
            send_mail(
                subject="Reset your password",
                message=render_to_string("accounts/emails/reset_password.txt", context),
                from_email=None,
                recipient_list=[email],
                html_message=render_to_string(
                    "accounts/emails/reset_password.html", context
                ),
            )

            messages.success(
                request, "Password reset instructions have been sent to your email."
            )
            return redirect("accounts:login")

        return self.render_to_response({"form": form})


class PasswordResetConfirmView(TemplateView):
    template_name = "accounts/password_reset_confirm.html"
    form_class = PasswordResetConfirmForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token = self.kwargs.get("token")
        reset = get_object_or_404(PasswordReset, token=token)

        if not reset.is_valid():
            messages.error(
                self.request, "This password reset link has expired or been used."
            )
            return redirect("accounts:password_reset_request")

        context["form"] = self.form_class()
        context["token"] = token
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        token = kwargs.get("token")
        reset = get_object_or_404(PasswordReset, token=token)

        if not reset.is_valid():
            messages.error(
                request, "This password reset link has expired or been used."
            )
            return redirect("accounts:password_reset_request")

        if form.is_valid():
            user = reset.user
            user.set_password(form.cleaned_data["new_password1"])
            user.save()

            reset.used = True
            reset.save()

            messages.success(request, "Your password has been reset successfully.")
            return redirect("accounts:login")

        return self.render_to_response({"form": form, "token": token})
