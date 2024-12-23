from rest_framework import serializers
from apps.blog.models import Article, Category, Comment
from apps.accounts.models import CustomUser
from django.contrib.auth import get_user_model
from taggit.serializers import TagListSerializerField

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "article_count"]

    def get_article_count(self, obj):
        return obj.articles.filter(status="published").count()


class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagListSerializerField()
    reading_time = serializers.IntegerField(read_only=True)
    comment_count = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "featured_image",
            "author",
            "category",
            "tags",
            "status",
            "view_count",
            "reading_time",
            "comment_count",
            "is_bookmarked",
            "created_at",
            "updated_at",
            "published_at",
        ]
        read_only_fields = ["slug", "view_count", "created_at", "updated_at"]

    def get_comment_count(self, obj):
        return obj.comments.filter(is_approved=True).count()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user.bookmarks.filter(article=obj).exists()
        return False


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "article",
            "user",
            "content",
            "parent",
            "replies",
            "created_at",
            "updated_at",
            "is_approved",
        ]
        read_only_fields = ["is_approved"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []


class CustomUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    article_count = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "user",
            "bio",
            "avatar",
            "location",
            "website",
            "github",
            "twitter",
            "linkedin",
            "article_count",
            "total_views",
        ]

    def get_article_count(self, obj):
        return obj.user.articles.filter(status="published").count()

    def get_total_views(self, obj):
        return sum(article.view_count for article in obj.user.articles.all())
