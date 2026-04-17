import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.common.api.v1.services import record_audit_event


@pytest.mark.django_db
def test_outbox_health_snapshot_command_returns_json_payload():
    output = StringIO()

    call_command("outbox_health_snapshot", stdout=output)

    payload = json.loads(output.getvalue())
    assert "pending_total" in payload
    assert "failed_total" in payload


@pytest.mark.django_db
def test_common_platform_slo_report_returns_summary():
    record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    output = StringIO()

    call_command("common_platform_slo_report", stdout=output)

    payload = json.loads(output.getvalue())
    assert "check_passed" in payload
    assert "idempotency_cleaned_records" in payload


@pytest.mark.django_db
def test_common_platform_check_can_fail_on_error_without_fresh_integrity():
    output = StringIO()

    with pytest.raises(CommandError):
        call_command("common_platform_check", stdout=output, fail_on_error=True)
