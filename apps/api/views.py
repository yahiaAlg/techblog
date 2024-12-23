import uuid

# Create your views here.
from apps.api.forms import APIKeyForm, APIKeyRegenerationForm
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import APIKey, APIRequest, APIRateLimit
from .serializers import (
    ArticleSerializer,
    CategorySerializer,
    CommentSerializer,
    CustomUserSerializer,
)
from apps.blog.models import Article, Category, Comment
from apps.accounts.models import CustomUser
from .permissions import HasValidAPIKey
from .throttling import APIKeyThrottle
import time
from django.db.models import Q


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    pagination_class = CustomPagination
    permission_classes = [HasValidAPIKey]
    throttle_classes = [APIKeyThrottle]

    def get_queryset(self):
        queryset = Article.objects.filter(status="published")

        # Apply filters
        category = self.request.query_params.get("category", None)
        if category:
            queryset = queryset.filter(category__slug=category)

        tag = self.request.query_params.get("tag", None)
        if tag:
            queryset = queryset.filter(tags__slug=tag)

        author = self.request.query_params.get("author", None)
        if author:
            queryset = queryset.filter(author__username=author)

        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(content__icontains=search)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        start_time = time.time()
        response = super().list(request, *args, **kwargs)
        end_time = time.time()

        # Log API request
        APIRequest.objects.create(
            api_key=request.auth,
            endpoint="articles-list",
            method=request.method,
            status_code=response.status_code,
            response_time=(end_time - start_time) * 1000,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return response

    @action(detail=True, methods=["post"])
    def bookmark(self, request, pk=None):
        article = self.get_object()
        user = request.user

        if user.bookmarks.filter(article=article).exists():
            user.bookmarks.filter(article=article).delete()
            return Response({"status": "unbookmarked"})
        else:
            user.bookmarks.create(article=article)
            return Response({"status": "bookmarked"})


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [HasValidAPIKey]
    throttle_classes = [APIKeyThrottle]


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [HasValidAPIKey]
    throttle_classes = [APIKeyThrottle]

    def get_queryset(self):
        return Comment.objects.filter(is_approved=True)

    @action(detail=True, methods=["post"])
    def reply(self, request, pk=None):
        parent_comment = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save(
                user=request.user, article=parent_comment.article, parent=parent_comment
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [HasValidAPIKey]
    throttle_classes = [APIKeyThrottle]
    lookup_field = "user__username"

    @action(detail=True, methods=["get"])
    def articles(self, request, user__username=None):
        profile = self.get_object()
        articles = Article.objects.filter(author=profile.user, status="published")
        page = self.paginate_queryset(articles)

        if page is not None:
            serializer = ArticleSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)


class APIKeyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def generate(self, request):
        form = APIKeyForm(request.POST)
        if form.is_valid():
            api_key = form.save(commit=False)
            api_key.user = request.user
            api_key.save()

            # Create default rate limits
            APIRateLimit.objects.create(api_key=api_key)

            return Response({"key": api_key.key, "name": api_key.name})
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        api_key = self.get_object()
        form = APIKeyRegenerationForm(request.POST)

        if form.is_valid():
            api_key.key = uuid.uuid4()
            api_key.save()
            return Response({"key": api_key.key})
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
