from rest_framework.permissions import BasePermission


class IsStaffNotificationWriter(BasePermission):
    message = "Only staff users can create notifications."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        return bool(user and user.is_authenticated and user.is_staff)
