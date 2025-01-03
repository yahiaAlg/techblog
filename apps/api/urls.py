from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r'articles', views.ArticleViewSet, basename='article')
router.register(r'categories', views.CategoryViewSet)
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'api-keys', views.APIKeyViewSet, basename='api-key')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='api:schema'), name='redoc'),
    path('auth/', include('rest_framework.urls')),
]