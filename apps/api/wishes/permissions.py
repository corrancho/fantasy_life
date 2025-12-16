from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsMatchParticipant(permissions.BasePermission):
    """
    Custom permission to only allow participants in a match to view/edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Check if user is either user1 or user2 in the match
        return obj.user1 == request.user or obj.user2 == request.user
