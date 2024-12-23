from rest_framework import permissions
from django.utils import timezone

class HasValidAPIKey(permissions.BasePermission):
    message = "Invalid or expired API key."

    def has_permission(self, request, view):
        api_key = request.auth
        if not api_key:
            return False
        return api_key.is_active and api_key.user.is_active

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Write permissions are only allowed to the owner
        return obj.user == request.user

class IsArticleAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.author == request.user

class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return obj.user == request.user