from .common import ValidationError


class InvalidAuditEvent(ValidationError):
    """Wird geworfen, wenn ein Audit-Event unvollstaendige Kerndaten enthaelt."""

    code = "invalid_audit_event"
    default_message = "The audit event payload is invalid."

