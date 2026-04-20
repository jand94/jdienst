from rest_framework.permissions import BasePermission

from apps.accounts.api.v1.services import log_permission_denied
from apps.common.api.v1.services import is_audit_operator
from apps.common.api.v1.services import extract_audit_correlation_ids


class IsStaffNotificationWriter(BasePermission):
    message = "Only staff users can create notifications."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_permission_denied(
            actor=user,
            resource="notification.create",
            source="api",
            request_id=request_id,
            trace_id=trace_id,
            metadata={
                "action": getattr(view, "action", "unknown"),
                "reason": "missing_staff_role",
            },
        )
        return False


class IsNotificationOperator(BasePermission):
    message = "Only notification operators can access this endpoint."

    def has_permission(self, request, view):
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser or user.is_staff or is_audit_operator(user):
            return True
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_permission_denied(
            actor=user,
            resource="notification.ops.read",
            source="api",
            request_id=request_id,
            trace_id=trace_id,
            metadata={
                "action": getattr(view, "action", "unknown"),
                "reason": "missing_operator_role",
            },
        )
        return False
