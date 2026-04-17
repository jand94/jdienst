from rest_framework.permissions import BasePermission

from apps.accounts.api.v1.services import log_permission_denied


class IsAuditReader(BasePermission):
    message = "Audit reader permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.has_perm("common.view_auditevent"):
            return True

        log_permission_denied(
            actor=user,
            resource="common.audit_event.read",
            source="api",
            metadata={"reason": "missing_common.view_auditevent"},
        )
        return False
