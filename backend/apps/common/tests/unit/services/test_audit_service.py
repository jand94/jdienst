import pytest

from apps.common.api.v1.services.audit_service import record_audit_event
from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_record_audit_event_persists_expected_fields():
    actor = UserFactory()

    event = record_audit_event(
        action="entity.updated",
        target_model="accounts.User",
        target_id=str(actor.pk),
        actor=actor,
        metadata={"source": "unit-test"},
    )

    assert isinstance(event, AuditEvent)
    assert event.actor_id == actor.id
    assert event.action == "entity.updated"
    assert event.target_model == "accounts.User"
    assert event.target_id == str(actor.pk)
    assert event.metadata == {"source": "unit-test"}


@pytest.mark.django_db
def test_record_audit_event_redacts_sensitive_metadata_keys():
    event = record_audit_event(
        action="auth.login",
        target_model="accounts.User",
        target_id="42",
        metadata={
            "source": "api",
            "token": "secret-token",
            "password": "top-secret",
            "nested": {
                "authorization": "Bearer abc",
                "safe": "ok",
            },
        },
    )

    assert event.metadata == {
        "source": "api",
        "nested": {"safe": "ok"},
    }
