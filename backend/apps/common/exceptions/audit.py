from .common import ValidationError
from apps.common.constants import ErrorCode


class InvalidAuditEvent(ValidationError):
    """Wird geworfen, wenn ein Audit-Event unvollstaendige Kerndaten enthaelt."""

    code = ErrorCode.INVALID_AUDIT_EVENT
    default_message = "The audit event payload is invalid."

