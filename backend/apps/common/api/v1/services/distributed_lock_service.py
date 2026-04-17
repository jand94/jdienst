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


def acquire_lock(*, key: str, owner: str, ttl_seconds: int = 30) -> str:
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
                    expires_at=expires_at,
                )
                return token
            except IntegrityError:
                raise ConflictError("Failed to acquire lock due to a concurrent claim.")

        if lock.expires_at <= now:
            lock.owner = owner
            lock.token = token
            lock.expires_at = expires_at
            lock.save(update_fields=("owner", "token", "expires_at", "updated_at"))
            return token

    raise ConflictError("Lock is currently held by another worker.", details={"key": key})


def release_lock(*, key: str, token: str) -> None:
    DistributedLock.objects.filter(key=key, token=token).delete()


def renew_lock(*, key: str, token: str, ttl_seconds: int = 30) -> None:
    updated = DistributedLock.objects.filter(key=key, token=token).update(
        expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
        updated_at=timezone.now(),
    )
    if updated == 0:
        raise ConflictError("Cannot renew a lock that is no longer held.", details={"key": key})


@contextmanager
def lock_scope(*, key: str, owner: str, ttl_seconds: int = 30):
    token = acquire_lock(key=key, owner=owner, ttl_seconds=ttl_seconds)
    try:
        yield token
    finally:
        release_lock(key=key, token=token)
