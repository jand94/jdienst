import pytest

from apps.common.api.v1.services.idempotency_service import execute_idempotent_operation
from apps.common.exceptions import ConflictError
from apps.common.models import IdempotencyKey
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_execute_idempotent_operation_replays_completed_result():
    user = UserFactory()

    first = execute_idempotent_operation(
        scope="accounts.user.me.deactivate",
        key="idem-1",
        actor=user,
        method="POST",
        path="/api/accounts/v1/users/me/deactivate/",
        body={},
        execute=lambda: ({"ok": True}, 200),
    )
    second = execute_idempotent_operation(
        scope="accounts.user.me.deactivate",
        key="idem-1",
        actor=user,
        method="POST",
        path="/api/accounts/v1/users/me/deactivate/",
        body={},
        execute=lambda: ({"ok": False}, 500),
    )

    assert first.replayed is False
    assert second.replayed is True
    assert second.payload == {"ok": True}
    assert IdempotencyKey.objects.count() == 1


@pytest.mark.django_db
def test_execute_idempotent_operation_rejects_fingerprint_conflict():
    user = UserFactory()
    execute_idempotent_operation(
        scope="accounts.user.me.patch",
        key="idem-2",
        actor=user,
        method="PATCH",
        path="/api/accounts/v1/users/me/",
        body={"first_name": "Alice"},
        execute=lambda: ({"id": 1}, 200),
    )

    with pytest.raises(ConflictError):
        execute_idempotent_operation(
            scope="accounts.user.me.patch",
            key="idem-2",
            actor=user,
            method="PATCH",
            path="/api/accounts/v1/users/me/",
            body={"first_name": "Bob"},
            execute=lambda: ({"id": 1}, 200),
        )
