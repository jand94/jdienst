import pytest
from django.core.exceptions import ValidationError

from apps.common.api.v1.services.audit_service import record_audit_event


@pytest.mark.django_db
def test_audit_event_integrity_chain_is_populated():
    first = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    second = record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="2",
        metadata={"source": "api"},
    )

    assert len(first.integrity_hash) == 64
    assert second.previous_hash == first.integrity_hash
    assert len(second.integrity_hash) == 64


@pytest.mark.django_db
def test_audit_event_is_append_only_after_creation():
    event = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )

    event.action = "auth.login.succeeded"
    with pytest.raises(ValidationError):
        event.save()

    with pytest.raises(ValidationError):
        event.delete()
