from django.db import models


class ErrorCode(models.TextChoices):
    COMMON_ERROR = "common_error", "Common error"
    VALIDATION_ERROR = "validation_error", "Validation error"
    CONFLICT_ERROR = "conflict_error", "Conflict error"
    INFRASTRUCTURE_ERROR = "infrastructure_error", "Infrastructure error"
    SECURITY_ERROR = "security_error", "Security error"
    INVALID_AUDIT_EVENT = "invalid_audit_event", "Invalid audit event"
    INTERNAL_ERROR = "internal_error", "Internal error"
    API_ERROR = "api_error", "API error"
