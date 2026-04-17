from datetime import timedelta

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone

from apps.common.api.v1.services.audit_service import record_audit_event
from apps.common.models import AuditEvent, AuditIntegrityVerification
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_audit_ops_health_snapshot_requires_operator_permission(api_client):
    user = UserFactory(is_staff=False)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("common-audit-ops-health-snapshot"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_audit_ops_health_snapshot_returns_payload_for_operator(api_client):
    operator = UserFactory(is_staff=True)
    operator.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
    record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="42",
        actor=operator,
        metadata={"source": "api"},
    )
    api_client.force_authenticate(user=operator)

    response = api_client.get(reverse("common-audit-ops-health-snapshot"), {"window_hours": 48})

    assert response.status_code == 200
    assert response.data["window_hours"] == 48
    assert "retention_class_counts" in response.data


@pytest.mark.django_db
def test_audit_ops_verify_integrity_creates_verification(api_client):
    operator = UserFactory(is_staff=True)
    operator.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
    record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="8",
        actor=operator,
        metadata={"source": "api"},
    )
    api_client.force_authenticate(user=operator)

    response = api_client.post(
        reverse("common-audit-ops-verify-integrity"),
        data={"create_checkpoint": True},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["status"] == AuditIntegrityVerification.STATUS_PASSED
    assert AuditEvent.objects.filter(action="common.audit_integrity.verified").exists()


@pytest.mark.django_db
def test_audit_ops_archive_events_supports_before_days(api_client):
    operator = UserFactory(is_staff=True)
    operator.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
    event = record_audit_event(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id="99",
        actor=operator,
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=event.pk).update(created_at=timezone.now() - timedelta(days=120))
    api_client.force_authenticate(user=operator)

    response = api_client.post(
        reverse("common-audit-ops-archive-events"),
        data={"before_days": 30},
        format="json",
    )

    assert response.status_code == 200
    event.refresh_from_db()
    assert response.data["mode"] == "before_days"
    assert event.archived_at is not None


@pytest.mark.django_db
def test_audit_ops_siem_export_preview_does_not_mark_events_exported(api_client):
    operator = UserFactory(is_staff=True)
    operator.user_permissions.add(Permission.objects.get(codename="view_auditevent"))
    event = record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="123",
        actor=operator,
        metadata={"source": "api"},
    )
    api_client.force_authenticate(user=operator)

    response = api_client.get(reverse("common-audit-ops-siem-export-preview"), {"limit": 10})

    assert response.status_code == 200
    assert response.data["exportable_count"] >= 1
    event.refresh_from_db()
    assert event.exported_at is None
