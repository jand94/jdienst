import pytest

from apps.accounts.api.v1.services.account_user_service import deactivate_user, update_user_profile
from apps.common.models import AuditEvent, OutboxEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_update_user_profile_updates_fields_and_writes_audit_event():
    actor = UserFactory(first_name="Old", last_name="Name")

    updated = update_user_profile(
        actor=actor,
        data={"first_name": "New", "last_name": "Last"},
        source="api",
    )

    actor.refresh_from_db()
    assert updated.first_name == "New"
    assert updated.last_name == "Last"
    event = AuditEvent.objects.filter(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id=str(actor.pk),
    ).first()
    assert event is not None
    assert event.metadata["source"] == "api"
    outbox = OutboxEvent.objects.filter(topic="accounts.user.updated", payload__user_id=str(actor.pk)).first()
    assert outbox is not None


@pytest.mark.django_db
def test_deactivate_user_sets_is_active_false_and_writes_audit_event():
    actor = UserFactory(is_active=True)

    deactivate_user(actor=actor, source="api")

    actor.refresh_from_db()
    assert actor.is_active is False
    event = AuditEvent.objects.filter(
        action="accounts.user.deactivated",
        target_model="accounts.User",
        target_id=str(actor.pk),
    ).first()
    assert event is not None
    assert event.metadata["source"] == "api"
    outbox = OutboxEvent.objects.filter(topic="accounts.user.deactivated", payload__user_id=str(actor.pk)).first()
    assert outbox is not None


@pytest.mark.django_db
def test_update_user_profile_writes_correlation_identifiers():
    actor = UserFactory(first_name="Old")

    update_user_profile(
        actor=actor,
        data={"first_name": "New"},
        source="api",
        request_id="req-99",
        trace_id="trace-99",
    )

    event = AuditEvent.objects.filter(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id=str(actor.pk),
    ).first()
    assert event is not None
    assert event.metadata["request_id"] == "req-99"
    assert event.metadata["trace_id"] == "trace-99"
