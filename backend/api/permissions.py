from rest_framework import permissions

class IsSelfOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or obj == request.user
        return False