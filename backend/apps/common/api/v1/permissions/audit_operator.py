from rest_framework.permissions import BasePermission

from apps.accounts.api.v1.services import log_permission_denied
from apps.common.api.v1.services import is_audit_reader


class IsAuditOperator(BasePermission):
    message = "Audit operator permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if is_audit_reader(user) and user.is_staff:
            return True

        log_permission_denied(
            actor=user,
            resource="common.audit_ops.execute",
            source="api",
            metadata={"action": getattr(view, "action", "unknown")},
        )
        return False
