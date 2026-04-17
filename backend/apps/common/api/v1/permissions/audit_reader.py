from rest_framework.permissions import BasePermission

from apps.accounts.api.v1.services import log_permission_denied
from apps.common.api.v1.services import is_audit_reader


class IsAuditReader(BasePermission):
    message = "Audit reader permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if is_audit_reader(user):
            return True

        log_permission_denied(
            actor=user,
            resource="common.audit_event.read",
            source="api",
            metadata={"reason": "missing_common.view_auditevent"},
        )
        return False
