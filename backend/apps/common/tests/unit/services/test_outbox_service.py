import pytest

from apps.common.api.v1.services.outbox_service import (
    collect_outbox_health_snapshot,
    dispatch_pending_outbox_events,
    enqueue_outbox_event,
)
from apps.common.models import OutboxEvent


@pytest.mark.django_db
def test_enqueue_outbox_event_creates_pending_record():
    event = enqueue_outbox_event(
        topic="accounts.user.updated",
        payload={"user_id": "1"},
        dedup_key="user-1-update",
    )

    assert event.status == OutboxEvent.STATUS_PENDING
    assert OutboxEvent.objects.filter(pk=event.pk).exists()


@pytest.mark.django_db
def test_dispatch_pending_outbox_events_marks_record_sent_without_handler():
    enqueue_outbox_event(
        topic="accounts.user.updated",
        payload={"user_id": "1"},
        dedup_key="user-1-update",
    )

    result = dispatch_pending_outbox_events(batch_size=50)

    assert result["processed"] == 1
    assert result["sent"] == 1
    assert OutboxEvent.objects.filter(status=OutboxEvent.STATUS_SENT).count() == 1


@pytest.mark.django_db
def test_collect_outbox_health_snapshot_returns_expected_counts():
    enqueue_outbox_event(topic="a", payload={})
    enqueue_outbox_event(topic="b", payload={})

    snapshot = collect_outbox_health_snapshot()

    assert snapshot["pending_total"] == 2
    assert snapshot["failed_total"] == 0
