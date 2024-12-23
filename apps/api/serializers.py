from rest_framework import serializers
from django.contrib.auth.models import User
from accounts.models import Profile
from apps.api.models import APIKey
from blog.models import Article, Category, Comment
from taggit.serializers import TagListSerializerField

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'date_joined']
        read_only_fields = ['date_joined']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user', 'bio', 'avatar', 'location', 'website',
            'github', 'twitter', 'linkedin', 'newsletter_subscription'
        ]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']

class ArticleSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'content', 'author',
            'category', 'tags', 'status', 'created_at',
            'updated_at', 'published_at', 'view_count'
        ]
        read_only_fields = ['slug', 'view_count', 'created_at', 'updated_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'article', 'user', 'content',
            'parent', 'replies', 'created_at'
        ]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

class APIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        fields = ['id', 'name', 'key', 'created_at', 'last_used_at', 'is_active']
        read_only_fields = ['key', 'created_at', 'last_used_at']