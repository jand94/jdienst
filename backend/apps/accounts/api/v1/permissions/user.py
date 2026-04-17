from rest_framework.permissions import BasePermission

from apps.accounts.api.v1.services import log_permission_denied


class IsSelfOrStaff(BasePermission):
    message = "You do not have permission to access this user."

    def has_object_permission(self, request, view, obj):
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return False
        if user.is_staff or user.pk == obj.pk:
            return True

        log_permission_denied(
            actor=user,
            resource="accounts.user.detail",
            source="api",
            metadata={"target_user_id": obj.pk},
        )
        return False


class IsStaffUser(BasePermission):
    message = "Staff permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if user and user.is_authenticated and user.is_staff:
            return True

        if user and user.is_authenticated:
            log_permission_denied(
                actor=user,
                resource="accounts.user.list",
                source="api",
            )
        return False
