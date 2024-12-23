from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from taggit.managers import TaggableManager
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models import Count
from django.utils import timezone
import readtime

User = get_user_model()


class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Image"), upload_to="categories/", blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent Category"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    type = models.CharField(
        _("Type"),
        max_length=50,
        choices=[
            ("programming", "Programming"),
            ("development", "Development"),
            ("design", "Design"),
        ],
        default="development",
    )
    level = models.CharField(
        _("Level"),
        max_length=20,
        choices=[
            ("beginner", "Beginner"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        default="intermediate",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    order = models.IntegerField(_("Order"), default=0)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})

    def get_article_count(self):
        return self.articles.count()

    @property
    def breadcrumb(self):
        items = []
        current = self
        while current:
            items.append(current)
            current = current.parent
        return reversed(items)


class Article(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    content = RichTextUploadingField(_("Content"))
    excerpt = models.TextField(_("Excerpt"), blank=True)
    featured_image = models.ImageField(_("Featured Image"), upload_to="articles/")
    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        on_delete=models.CASCADE,
        related_name="articles",
    )
    author = models.ForeignKey(
        User,
        verbose_name=_("Author"),
        on_delete=models.CASCADE,
        related_name="articles",
    )
    tags = TaggableManager()
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        default="draft",
    )
    featured = models.BooleanField(_("Featured"), default=False)
    view_count = models.PositiveIntegerField(_("View Count"), default=0)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    published_at = models.DateTimeField(_("Published At"), null=True, blank=True)

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["-published_at", "-created_at"]),
            models.Index(fields=["status", "featured"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.excerpt and self.content:
            self.excerpt = self.content[:200].replace("<p>", "").replace("</p>", "")
        if self.status == "published" and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    @property
    def reading_time(self):
        return readtime.of_text(self.content).minutes

    def get_related_articles(self):
        article_tags = self.tags.values_list("id", flat=True)
        return (
            Article.objects.filter(status="published", tags__in=article_tags)
            .exclude(id=self.id)
            .annotate(same_tags=Count("tags"))
            .order_by("-same_tags", "-published_at")[:3]
        )

    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])


class Comment(models.Model):
    article = models.ForeignKey(
        Article,
        verbose_name=_("Article"),
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self",
        verbose_name=_("Parent Comment"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    content = models.TextField(_("Content"))
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    is_approved = models.BooleanField(_("Is Approved"), default=False)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, verbose_name=_("User"), on_delete=models.CASCADE, related_name="profile"
    )
    bio = models.TextField(_("Bio"), blank=True)
    avatar = models.ImageField(_("Avatar"), upload_to="avatars/", blank=True)
    location = models.CharField(_("Location"), max_length=100, blank=True)
    website = models.URLField(_("Website"), max_length=200, blank=True)
    github = models.URLField(_("GitHub"), max_length=200, blank=True)
    twitter = models.URLField(_("Twitter"), max_length=200, blank=True)
    linkedin = models.URLField(_("LinkedIn"), max_length=200, blank=True)
    newsletter_subscription = models.BooleanField(
        _("Newsletter Subscription"), default=False
    )

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"Profile of {self.user.username}"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return f"https://ui-avatars.com/api/?name={self.user.get_full_name()}&size=128"


class Bookmark(models.Model):
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, related_name="bookmarks"
    )
    article = models.ForeignKey(
        Article,
        verbose_name=_("Article"),
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Bookmark")
        verbose_name_plural = _("Bookmarks")
        unique_together = ["user", "article"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"


class SearchQuery(models.Model):
    query = models.CharField(_("Query"), max_length=200)
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="search_queries",
    )
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    results_count = models.IntegerField(_("Results Count"))

    class Meta:
        verbose_name = _("Search Query")
        verbose_name_plural = _("Search Queries")
        ordering = ["-created_at"]

    def __str__(self):
        return self.query


class NewsletterSubscriber(models.Model):
    email = models.EmailField(_("Email"), unique=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Newsletter Subscriber")
        verbose_name_plural = _("Newsletter Subscribers")
        ordering = ["-created_at"]

    def __str__(self):
        return self.email
