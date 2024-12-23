from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Article, Comment, UserProfile, NewsletterSubscriber
import re


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            "title",
            "content",
            "excerpt",
            "featured_image",
            "category",
            "tags",
            "status",
            "featured",
        ]
        widgets = {
            "content": CKEditorUploadingWidget(config_name="advanced"),
            "excerpt": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"]
        if (
            Article.objects.filter(title__iexact=title)
            .exclude(id=self.instance.id)
            .exists()
        ):
            raise ValidationError(_("An article with this title already exists."))
        return title

    def clean_content(self):
        content = self.cleaned_data["content"]
        # Remove potentially harmful HTML tags
        content = re.sub(r"<script.*?</script>", "", content, flags=re.DOTALL)
        return content

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        content = cleaned_data.get("content")
        featured_image = cleaned_data.get("featured_image")

        if status == "published":
            if not content or len(content) < 100:
                raise ValidationError(
                    _(
                        "Published articles must have at least 100 characters of content."
                    )
                )
            if not featured_image:
                raise ValidationError(
                    _("Published articles must have a featured image.")
                )

        return cleaned_data


class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 4, "placeholder": _("Write your comment here...")}
            )
        }

    def clean_content(self):
        content = self.cleaned_data["content"]
        if len(content) < 2:
            raise ValidationError(_("Comment must be at least 2 characters long."))
        return content


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "bio",
            "location",
            "website",
            "github",
            "twitter",
            "linkedin",
            "newsletter_subscription",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email

    def clean_website(self):
        website = self.cleaned_data["website"]
        if website and not website.startswith(("http://", "https://")):
            website = "https://" + website
        return website

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            # Save user info
            user = profile.user
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            user.save()
            profile.save()
        return profile


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(
                attrs={"placeholder": _("Enter your email address")}
            )
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if NewsletterSubscriber.objects.filter(email=email).exists():
            raise ValidationError(
                _("This email is already subscribed to our newsletter.")
            )
        return email


class SearchForm(forms.Form):
    q = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search articles, tutorials, and more..."),
                "class": "form-control form-control-lg",
            }
        ),
    )
    category = forms.MultipleChoiceField(
        required=False, widget=forms.CheckboxSelectMultiple
    )
    tag = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple)
    date_range = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": _("Select date range")}
        ),
    )
    sort = forms.ChoiceField(
        choices=[
            ("relevance", _("Relevance")),
            ("date", _("Date")),
            ("views", _("Views")),
        ],
        required=False,
        initial="relevance",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category, Article
        from taggit.models import Tag

        # Dynamically populate category choices
        self.fields["category"].choices = [
            (c.slug, c.name) for c in Category.objects.all()
        ]

        # Dynamically populate tag choices
        self.fields["tag"].choices = [(t.slug, t.name) for t in Tag.objects.all()]
