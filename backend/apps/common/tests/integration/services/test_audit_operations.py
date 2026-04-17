import json
from io import StringIO
from datetime import timedelta

import pytest
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
    assert event.exported_at is not None
