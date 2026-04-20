from rest_framework.permissions import BasePermission

from apps.common.api.v1.services import extract_audit_correlation_ids, is_audit_operator, log_permission_denied


class IsAuditOperator(BasePermission):
    message = "Audit operator permission is required."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if is_audit_operator(user):
            return True

        request_id, trace_id = extract_audit_correlation_ids(request)
        log_permission_denied(
            actor=user,
            resource="common.audit_ops.execute",
            source="api",
            request_id=request_id,
            trace_id=trace_id,
            metadata={
                "action": getattr(view, "action", "unknown"),
                "reason": "missing_common.operate_auditevent",
            },
        )
        return False
