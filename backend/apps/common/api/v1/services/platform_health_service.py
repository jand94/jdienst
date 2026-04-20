from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.common.api.v1.services.audit_operations_service import collect_audit_health_snapshot
from apps.common.api.v1.services.idempotency_service import (
    cleanup_expired_idempotency_keys,
    collect_idempotency_health_snapshot,
)
from apps.common.api.v1.services.outbox_service import collect_outbox_health_snapshot
from apps.common.api.v1.services.platform_settings_service import get_platform_settings
from apps.common.models import Tenant, TenantMembership


def collect_tenant_consistency_snapshot() -> dict:
    inconsistent = TenantMembership.objects.filter(tenant__deleted_at__isnull=False, is_active=True).count()
    return {
        "active_memberships_on_deleted_tenants": inconsistent,
        "tenant_count": Tenant.all_objects.count(),
        "passed": inconsistent == 0,
    }


def cleanup_soft_deleted_tenants(*, older_than_days: int = 30) -> int:
    threshold = timezone.now() - timedelta(days=older_than_days)
    deleted_count, _ = Tenant.deleted_objects.filter(deleted_at__lt=threshold).hard_delete()
    return deleted_count


def collect_platform_health_snapshot(*, window_hours: int = 24) -> dict:
    audit_snapshot = collect_audit_health_snapshot(window_hours=window_hours)
    notification_snapshot = None
    try:
        from apps.notification.api.v1.services.notification_health_service import collect_notification_health_snapshot

        notification_snapshot = collect_notification_health_snapshot(window_hours=window_hours)
    except Exception:  # noqa: BLE001
        notification_snapshot = None
    return {
        "window_hours": window_hours,
        "audit": audit_snapshot,
        "idempotency": collect_idempotency_health_snapshot(),
        "outbox": collect_outbox_health_snapshot(),
        "tenant": collect_tenant_consistency_snapshot(),
        "notification": notification_snapshot,
    }


def run_platform_check(*, window_hours: int = 24) -> dict:
    settings_values = get_platform_settings()
    snapshot = collect_platform_health_snapshot(window_hours=window_hours)
    checks = []
    audit = snapshot["audit"]
    tenant_snapshot = collect_tenant_consistency_snapshot()
    active_tenant_count = Tenant.objects.filter(status=Tenant.STATUS_ACTIVE).count()
    checks.append(
        {
            "name": "audit_verification_fresh",
            "passed": bool(audit["integrity_verification"]["is_fresh"]) or int(audit["events_total"]) == 0,
            "details": {
                **audit["integrity_verification"],
                "events_total": audit["events_total"],
            },
        }
    )
    outbox = snapshot["outbox"]
    checks.append(
        {
            "name": "outbox_pending_limit",
            "passed": outbox["pending_total"] <= settings_values.max_outbox_pending,
            "details": outbox,
        }
    )
    checks.append(
        {
            "name": "outbox_oldest_pending_age",
            "passed": outbox["oldest_pending_age_seconds"] <= settings_values.max_outbox_oldest_age_seconds,
            "details": outbox,
        }
    )
    checks.append(
        {
            "name": "tenant_membership_consistency",
            "passed": tenant_snapshot["passed"],
            "details": tenant_snapshot,
        }
    )
    checks.append(
        {
            "name": "tenant_active_available",
            "passed": active_tenant_count > 0 or tenant_snapshot["tenant_count"] == 0,
            "details": {
                "active_tenant_count": active_tenant_count,
                "tenant_count": tenant_snapshot["tenant_count"],
            },
        }
    )
    notification_snapshot = snapshot.get("notification")
    if notification_snapshot:
        checks.append(
            {
                "name": "notification_pipeline_health",
                "passed": bool(notification_snapshot.get("passed", False)),
                "details": notification_snapshot,
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
    soft_deleted_cleaned = cleanup_soft_deleted_tenants()
    return {
        "window_hours": window_hours,
        "check_passed": check_result["passed"],
        "idempotency_cleaned_records": cleaned,
        "soft_deleted_tenants_cleaned": soft_deleted_cleaned,
        "check_summary": check_result["checks"],
    }
