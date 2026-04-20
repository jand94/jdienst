from rest_framework.permissions import BasePermission

from apps.common.api.v1.services import extract_audit_correlation_ids, is_audit_reader, log_permission_denied


class IsAuditReader(BasePermission):
    message = "Audit reader permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if is_audit_reader(user):
            return True

        request_id, trace_id = extract_audit_correlation_ids(request)
        log_permission_denied(
            actor=user,
            resource="common.audit_event.read",
            source="api",
            request_id=request_id,
            trace_id=trace_id,
            metadata={
                "reason": "missing_common.view_auditevent",
            },
        )
        return False
