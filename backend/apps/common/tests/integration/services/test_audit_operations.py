import json
from io import StringIO
from datetime import timedelta

import pytest
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.utils import timezone

from apps.common.api.v1.services.audit_service import record_audit_event
from apps.common.models import AuditEvent


@pytest.mark.django_db
def test_audit_archive_events_marks_old_entries_as_archived():
    event = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=event.pk).update(
        created_at=timezone.now() - timedelta(days=90),
    )

    call_command("audit_archive_events", before_days=30)
    event.refresh_from_db()

    assert event.archived_at is not None


@pytest.mark.django_db
def test_audit_export_siem_streams_json_and_marks_exported():
    event = record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="4",
        metadata={"source": "api"},
    )
    output = StringIO()

    call_command("audit_export_siem", stdout=output, limit=100, mark_exported=True)

    lines = [line for line in output.getvalue().splitlines() if line.strip()]
    payload = json.loads(lines[0])
    event.refresh_from_db()

    assert payload["id"] == str(event.pk)
    assert payload["action"] == "security.permission.denied"
    assert payload["retention_class"] == "security"
    assert event.exported_at is not None


@pytest.mark.django_db
def test_audit_archive_events_supports_retention_policy():
    security_event = record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="2",
        metadata={"source": "api"},
    )
    operational_event = record_audit_event(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id="3",
        metadata={"source": "api"},
    )
    old_timestamp = timezone.now() - timedelta(days=3700)
    AuditEvent.objects.filter(pk__in=[security_event.pk, operational_event.pk]).update(
        created_at=old_timestamp,
    )

    call_command("audit_archive_events", use_retention_policy=True)

    security_event.refresh_from_db()
    operational_event.refresh_from_db()
    assert security_event.archived_at is not None
    assert operational_event.archived_at is not None


@pytest.mark.django_db
def test_audit_verify_integrity_command_creates_verification():
    record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="11",
        metadata={"source": "api"},
    )
    output = StringIO()

    call_command("audit_verify_integrity", stdout=output, create_checkpoint=True)

    assert "status=passed" in output.getvalue()
    assert AuditEvent.objects.filter(action="common.audit_integrity.verified").exists()


@pytest.mark.django_db
def test_audit_setup_roles_assigns_audit_view_permission():
    output = StringIO()
    call_command("audit_setup_roles", stdout=output)

    group = Group.objects.get(name="AuditReader")
    permission = Permission.objects.get(codename="view_auditevent")

    assert permission in group.permissions.all()


@pytest.mark.django_db
def test_audit_health_snapshot_command_returns_json_payload():
    record_audit_event(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id="21",
        metadata={"source": "api"},
    )
    output = StringIO()

    call_command("audit_health_snapshot", stdout=output, window_hours=72)

    payload = json.loads(output.getvalue())
    assert payload["window_hours"] == 72
    assert "retention_class_counts" in payload


@pytest.mark.django_db
def test_audit_backfill_integrity_hashes_command_repairs_legacy_events():
    event = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="77",
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=event.pk).update(integrity_hash="")
    output = StringIO()

    call_command("audit_backfill_integrity_hashes", stdout=output)

    result = json.loads(output.getvalue())
    event.refresh_from_db()
    assert result["corrected_events"] >= 1
    assert event.integrity_hash != ""
