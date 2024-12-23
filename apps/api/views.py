from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import APIKey, APIRequest
from .serializers import (
    UserSerializer, ProfileSerializer, ArticleSerializer,
    CategorySerializer, CommentSerializer, APIKeySerializer
)
from .permissions import (
    HasValidAPIKey, IsOwnerOrReadOnly,
    IsArticleAuthorOrReadOnly, IsProfileOwnerOrReadOnly
)
from .throttling import APIKeyThrottle
from blog.models import Article, Category, Comment
from accounts.models import Profile
import time

class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [HasValidAPIKey]
    throttle_classes = [APIKeyThrottle]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def finalize_response(self, request, response, *args, **kwargs):
        # Record API request
        if hasattr(request, 'auth') and isinstance(request.auth, APIKey):
            APIRequest.objects.create(
                api_key=request.auth,
                endpoint=request.path,
                method=request.method,
                status_code=response.status_code,
                response_time=time.time() - request.start_time,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        return response

class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        user = self.get_object()
        articles = Article.objects.filter(author=user, status='published')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

class ProfileViewSet(BaseModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [HasValidAPIKey, IsProfileOwnerOrReadOnly]
    search_fields = ['user__username', 'location']
    ordering_fields = ['user__date_joined']

class ArticleViewSet(BaseModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [HasValidAPIKey, IsArticleAuthorOrReadOnly]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'view_count']

    def get_queryset(self):
        queryset = Article.objects.all()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(Q(status='published') | Q(author=self.request.user))

    @action(detail=True, methods=['post'])
    def toggle_bookmark(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if user.bookmarks.filter(article=article).exists():
            user.bookmarks.filter(article=article).delete()
            return Response({'status': 'unbookmarked'})
        user.bookmarks.create(article=article)
        return Response({'status': 'bookmarked'})

class CategoryViewSet(BaseModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class CommentViewSet(BaseModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [HasValidAPIKey, IsOwnerOrReadOnly]
    search_fields = ['content']
    ordering_fields = ['created_at']

    def get_queryset(self):
        return Comment.objects.filter(is_approved=True)

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        parent_comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                user=request.user,
                article=parent_comment.article,
                parent=parent_comment
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return APIKey.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        api_key = self.get_object()
        api_key.key = uuid.uuid4()
        api_key.save()
        return Response({
            'message': 'API key regenerated successfully',
            'key': api_key.key
        })

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        api_key = self.get_object()
        api_key.is_active = False
        api_key.save()
        return Response({'message': 'API key deactivated successfully'})