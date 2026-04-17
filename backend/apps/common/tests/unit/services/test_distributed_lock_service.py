import pytest

from apps.common.api.v1.services.distributed_lock_service import acquire_lock, release_lock, renew_lock
from apps.common.exceptions import ConflictError


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
