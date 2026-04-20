import pytest

from apps.common.api.v1.services.security_audit_service import log_permission_denied
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_log_permission_denied_creates_security_event():
    actor = UserFactory()

    event = log_permission_denied(
        actor=actor,
        resource="common.audit_event.read",
        source="api",
    )

    assert event.action == "security.permission.denied"
    assert event.target_model == "accounts.User"
    assert event.target_id == str(actor.pk)
    assert event.metadata["resource"] == "common.audit_event.read"
    assert event.metadata["source"] == "api"
