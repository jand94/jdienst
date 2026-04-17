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
    return {
        "window_hours": window_hours,
        "audit": audit_snapshot,
        "idempotency": collect_idempotency_health_snapshot(),
        "outbox": collect_outbox_health_snapshot(),
        "tenant": collect_tenant_consistency_snapshot(),
    }


def run_platform_check(*, window_hours: int = 24) -> dict:
    settings_values = get_platform_settings()
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
            "passed": collect_tenant_consistency_snapshot()["passed"],
            "details": collect_tenant_consistency_snapshot(),
        }
    )
    checks.append(
        {
            "name": "tenant_active_available",
            "passed": Tenant.objects.filter(status=Tenant.STATUS_ACTIVE).exists(),
            "details": {
                "active_tenant_count": Tenant.objects.filter(status=Tenant.STATUS_ACTIVE).count(),
            },
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
