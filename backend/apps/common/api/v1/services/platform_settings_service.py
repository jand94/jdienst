from __future__ import annotations

from dataclasses import dataclass

from django.conf import settings

from apps.common.exceptions import InfrastructureError


@dataclass(frozen=True)
class PlatformSettings:
    max_outbox_pending: int
    max_outbox_oldest_age_seconds: int
    max_audit_verification_age_hours: int
    outbox_max_attempts: int
    idempotency_retention_seconds: int
    tenant_header_required: bool


def get_platform_settings() -> PlatformSettings:
    values = PlatformSettings(
        max_outbox_pending=int(getattr(settings, "COMMON_PLATFORM_MAX_OUTBOX_PENDING", 5000)),
        max_outbox_oldest_age_seconds=int(
            getattr(settings, "COMMON_PLATFORM_MAX_OUTBOX_OLDEST_AGE_SECONDS", 900)
        ),
        max_audit_verification_age_hours=int(
            getattr(settings, "COMMON_PLATFORM_MAX_AUDIT_VERIFICATION_AGE_HOURS", 24)
        ),
        outbox_max_attempts=int(getattr(settings, "COMMON_OUTBOX_MAX_ATTEMPTS", 10)),
        idempotency_retention_seconds=int(
            getattr(settings, "COMMON_IDEMPOTENCY_RETENTION_SECONDS", 86400)
        ),
        tenant_header_required=bool(getattr(settings, "COMMON_TENANT_HEADER_REQUIRED", True)),
    )
    if values.max_outbox_pending < 0 or values.max_outbox_oldest_age_seconds < 0:
        raise InfrastructureError("COMMON_PLATFORM_* values must be non-negative.")
    if values.max_audit_verification_age_hours < 1:
        raise InfrastructureError("COMMON_PLATFORM_MAX_AUDIT_VERIFICATION_AGE_HOURS must be >= 1.")
    if values.outbox_max_attempts < 1:
        raise InfrastructureError("COMMON_OUTBOX_MAX_ATTEMPTS must be >= 1.")
    if values.idempotency_retention_seconds < 60:
        raise InfrastructureError("COMMON_IDEMPOTENCY_RETENTION_SECONDS must be >= 60.")
    return values
