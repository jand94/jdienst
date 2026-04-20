from __future__ import annotations

import uuid
from contextlib import contextmanager
from datetime import timedelta

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.common.exceptions import ConflictError
from apps.common.models import DistributedLock


def _build_token() -> str:
    return uuid.uuid4().hex


def acquire_lock_with_fencing(*, key: str, owner: str, ttl_seconds: int = 30) -> tuple[str, int]:
    now = timezone.now()
    expires_at = now + timedelta(seconds=ttl_seconds)
    token = _build_token()

    with transaction.atomic():
        lock = DistributedLock.objects.select_for_update().filter(key=key).first()
        if lock is None:
            try:
                DistributedLock.objects.create(
                    key=key,
                    owner=owner,
                    token=token,
                    fencing_counter=1,
                    expires_at=expires_at,
                )
                return token, 1
            except IntegrityError:
                raise ConflictError("Failed to acquire lock due to a concurrent claim.")

        if lock.expires_at <= now:
            lock.fencing_counter += 1
            lock.owner = owner
            lock.token = token
            lock.expires_at = expires_at
            lock.save(update_fields=("owner", "token", "fencing_counter", "expires_at", "updated_at"))
            return token, int(lock.fencing_counter)

    raise ConflictError("Lock is currently held by another worker.", details={"key": key})


def acquire_lock(*, key: str, owner: str, ttl_seconds: int = 30) -> str:
    token, _ = acquire_lock_with_fencing(key=key, owner=owner, ttl_seconds=ttl_seconds)
    return token


def release_lock(*, key: str, token: str) -> None:
    DistributedLock.objects.filter(key=key, token=token).delete()


def renew_lock(*, key: str, token: str, ttl_seconds: int = 30) -> None:
    updated = DistributedLock.objects.filter(key=key, token=token).update(
        expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
        updated_at=timezone.now(),
    )
    if updated == 0:
        raise ConflictError("Cannot renew a lock that is no longer held.", details={"key": key})


def get_lock_fencing_counter(*, key: str, token: str) -> int:
    counter = DistributedLock.objects.filter(key=key, token=token).values_list("fencing_counter", flat=True).first()
    if counter is None:
        raise ConflictError("Cannot resolve fencing counter for a lock that is no longer held.", details={"key": key})
    return int(counter)


@contextmanager
def lock_scope(*, key: str, owner: str, ttl_seconds: int = 30):
    token = acquire_lock(key=key, owner=owner, ttl_seconds=ttl_seconds)
    try:
        yield token
    finally:
        release_lock(key=key, token=token)


@contextmanager
def lock_scope_with_fencing(*, key: str, owner: str, ttl_seconds: int = 30):
    token, fencing_counter = acquire_lock_with_fencing(key=key, owner=owner, ttl_seconds=ttl_seconds)
    try:
        yield token, fencing_counter
    finally:
        release_lock(key=key, token=token)
