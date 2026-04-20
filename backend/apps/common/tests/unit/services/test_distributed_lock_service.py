from datetime import timedelta

import pytest
from django.utils import timezone

from apps.common.api.v1.services.distributed_lock_service import (
    acquire_lock,
    acquire_lock_with_fencing,
    get_lock_fencing_counter,
    release_lock,
    renew_lock,
)
from apps.common.exceptions import ConflictError
from apps.common.models import DistributedLock


@pytest.mark.django_db
def test_acquire_lock_prevents_parallel_claim():
    token = acquire_lock(key="lock-a", owner="worker-a", ttl_seconds=30)

    with pytest.raises(ConflictError):
        acquire_lock(key="lock-a", owner="worker-b", ttl_seconds=30)

    release_lock(key="lock-a", token=token)


@pytest.mark.django_db
def test_renew_lock_requires_valid_token():
    token = acquire_lock(key="lock-b", owner="worker-a", ttl_seconds=30)
    renew_lock(key="lock-b", token=token, ttl_seconds=30)

    with pytest.raises(ConflictError):
        renew_lock(key="lock-b", token="wrong-token", ttl_seconds=30)


@pytest.mark.django_db
def test_acquire_lock_with_fencing_increments_counter_after_expiry():
    first_token, first_counter = acquire_lock_with_fencing(key="lock-c", owner="worker-a", ttl_seconds=1)
    DistributedLock.objects.filter(key="lock-c", token=first_token).update(
        expires_at=timezone.now() - timedelta(seconds=1),
    )

    second_token, second_counter = acquire_lock_with_fencing(key="lock-c", owner="worker-b", ttl_seconds=30)

    assert first_counter == 1
    assert second_counter == 2
    assert second_token != first_token
    assert get_lock_fencing_counter(key="lock-c", token=second_token) == 2
