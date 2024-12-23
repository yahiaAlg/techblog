from rest_framework import permissions
from django.utils import timezone


class HasValidAPIKey(permissions.BasePermission):
    message = "Invalid or expired API key."

    def has_permission(self, request, view):
        api_key = request.auth
        if not api_key:
            return False

        # Update last used timestamp
        api_key.last_used_at = timezone.now()
        api_key.save()

        return api_key.is_active


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsArticleAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow authors of an article to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsCommentAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow authors of a comment to edit it.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user
