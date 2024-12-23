# Register your models here.
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from .models import (
    Category,
    Article,
    Comment,
    UserProfile,
    Bookmark,
    SearchQuery,
    NewsletterSubscriber,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "slug",
        "parent",
        "type",
        "level",
        "article_count",
        "created_at",
    ]
    list_filter = ["type", "level", "parent"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order", "name"]

    def article_count(self, obj):
        return obj.articles.count()

    article_count.short_description = _("Articles")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(articles_count=Count("articles"))


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "featured",
        "view_count",
        "created_at",
    ]
    list_filter = ["status", "featured", "category", "author"]
    search_fields = ["title", "content", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "category")}),
        (_("Content"), {"fields": ("content", "excerpt", "featured_image", "tags")}),
        (_("Settings"), {"fields": ("status", "featured", "published_at")}),
        (_("Statistics"), {"fields": ("view_count",), "classes": ("collapse",)}),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new article
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["user", "article", "created_at", "is_approved", "parent"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["content", "user__username", "article__title"]
    raw_id_fields = ["user", "article", "parent"]
    actions = ["approve_comments", "unapprove_comments"]

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    approve_comments.short_description = _("Approve selected comments")

    def unapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)

    unapprove_comments.short_description = _("Unapprove selected comments")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "location", "website", "newsletter_subscription"]
    list_filter = ["newsletter_subscription"]
    search_fields = ["user__username", "user__email", "bio"]
    raw_id_fields = ["user"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ["user", "article", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "article__title"]
    raw_id_fields = ["user", "article"]


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ["query", "user", "results_count", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["query", "user__username"]
    raw_id_fields = ["user"]

    def has_add_permission(self, request):
        return False  # Prevent manual creation of search queries


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ["email", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["email"]
    actions = ["activate_subscribers", "deactivate_subscribers"]

    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)

    activate_subscribers.short_description = _("Activate selected subscribers")

    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)

    deactivate_subscribers.short_description = _("Deactivate selected subscribers")


# Register custom admin site settings
admin.site.site_header = _("TechBlog Administration")
admin.site.site_title = _("TechBlog Admin")
admin.site.index_title = _("Dashboard")


# Custom admin views
class ArticleStatisticsView(admin.ModelAdmin):
    change_list_template = "admin/article_statistics.html"

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            "total_articles": qs.count(),
            "published_articles": qs.filter(status="published").count(),
            "draft_articles": qs.filter(status="draft").count(),
            "total_views": qs.aggregate(total_views=Sum("view_count"))["total_views"],
            "avg_views": qs.aggregate(avg_views=Avg("view_count"))["avg_views"],
        }

        response.context_data.update(metrics)
        return response
