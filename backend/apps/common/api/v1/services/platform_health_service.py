from __future__ import annotations

from django.conf import settings

from apps.common.api.v1.services.audit_operations_service import collect_audit_health_snapshot
from apps.common.api.v1.services.idempotency_service import (
    cleanup_expired_idempotency_keys,
    collect_idempotency_health_snapshot,
)
from apps.common.api.v1.services.outbox_service import collect_outbox_health_snapshot


def collect_platform_health_snapshot(*, window_hours: int = 24) -> dict:
    audit_snapshot = collect_audit_health_snapshot(window_hours=window_hours)
    return {
        "window_hours": window_hours,
        "audit": audit_snapshot,
        "idempotency": collect_idempotency_health_snapshot(),
        "outbox": collect_outbox_health_snapshot(),
    }


def run_platform_check(*, window_hours: int = 24) -> dict:
    snapshot = collect_platform_health_snapshot(window_hours=window_hours)
    checks = []
    checks.append(
        {
            "name": "audit_verification_fresh",
            "passed": bool(snapshot["audit"]["integrity_verification"]["is_fresh"]),
            "details": snapshot["audit"]["integrity_verification"],
        }
    )
    outbox = snapshot["outbox"]
    checks.append(
        {
            "name": "outbox_pending_limit",
            "passed": outbox["pending_total"] <= int(getattr(settings, "COMMON_PLATFORM_MAX_OUTBOX_PENDING", 5000)),
            "details": outbox,
        }
    )
    checks.append(
        {
            "name": "outbox_oldest_pending_age",
            "passed": outbox["oldest_pending_age_seconds"]
            <= int(getattr(settings, "COMMON_PLATFORM_MAX_OUTBOX_OLDEST_AGE_SECONDS", 900)),
            "details": outbox,
        }
    )
    passed = all(item["passed"] for item in checks)
    return {
        "passed": passed,
        "checks": checks,
        "snapshot": snapshot,
    }


def run_platform_slo_report(*, window_hours: int = 24) -> dict:
    check_result = run_platform_check(window_hours=window_hours)
    cleaned = cleanup_expired_idempotency_keys()
    return {
        "window_hours": window_hours,
        "check_passed": check_result["passed"],
        "idempotency_cleaned_records": cleaned,
        "check_summary": check_result["checks"],
    }
