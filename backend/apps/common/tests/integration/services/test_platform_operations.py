import json
from io import StringIO

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.common.api.v1.services import record_audit_event
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory


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
    record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )

    with pytest.raises(CommandError):
        call_command("common_platform_check", stdout=output, fail_on_error=True)


@pytest.mark.django_db
def test_tenant_consistency_check_command_reports_passed_state():
    tenant = TenantFactory()
    TenantMembershipFactory(user=UserFactory(), tenant=tenant)
    output = StringIO()

    call_command("tenant_consistency_check", stdout=output)

    payload = json.loads(output.getvalue())
    assert payload["passed"] is True


@pytest.mark.django_db
def test_soft_delete_retention_cleanup_command_outputs_payload():
    TenantFactory().soft_delete(reason="retention")
    output = StringIO()

    call_command("soft_delete_retention_cleanup", stdout=output, older_than_days=3650)

    payload = json.loads(output.getvalue())
    assert payload["model"] == "common.Tenant"
    assert "hard_deleted" in payload
