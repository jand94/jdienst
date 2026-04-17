import pytest

from apps.accounts.api.v1.services.account_security_service import (
    log_auth_attempt,
    log_permission_denied,
)
from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_log_auth_attempt_creates_failed_login_event():
    actor = UserFactory()

    event = log_auth_attempt(
        actor=actor,
        success=False,
        source="api",
        metadata={"email": "user@example.com"},
    )

    assert event.action == "auth.login.failed"
    assert event.target_model == "accounts.User"
    assert event.target_id == str(actor.pk)
    assert event.metadata["source"] == "api"
    assert event.metadata["result"] == "failed"
    assert AuditEvent.objects.filter(pk=event.pk).exists()


@pytest.mark.django_db
def test_log_permission_denied_creates_event_with_resource():
    actor = UserFactory()

    event = log_permission_denied(
        actor=actor,
        resource="common.audit_event.list",
        source="api",
    )

    assert event.action == "security.permission.denied"
    assert event.metadata["resource"] == "common.audit_event.list"
    assert event.metadata["source"] == "api"


@pytest.mark.django_db
def test_log_auth_attempt_persists_correlation_identifiers():
    actor = UserFactory()

    event = log_auth_attempt(
        actor=actor,
        success=True,
        source="api",
        request_id="req-42",
        trace_id="trace-42",
    )

    assert event.metadata["request_id"] == "req-42"
    assert event.metadata["trace_id"] == "trace-42"
