from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Callable

from django.db import IntegrityError, transaction
from django.db.models import Count, Min, Q
from django.utils import timezone

from apps.common.constants import HeaderName
from apps.common.api.v1.services.platform_settings_service import get_platform_settings
from apps.common.exceptions import ConflictError, ValidationError
from apps.common.models import IdempotencyKey

IDEMPOTENCY_KEY_HEADER = HeaderName.IDEMPOTENCY_KEY.value
DEFAULT_IDEMPOTENCY_TTL_SECONDS = 3600


@dataclass(frozen=True)
class IdempotencyResult:
    payload: dict[str, Any]
    status_code: int
    replayed: bool


def build_request_fingerprint(*, method: str, path: str, body: dict[str, Any]) -> str:
    canonical = json.dumps(
        {
            "method": method.upper(),
            "path": path,
            "body": body,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def require_idempotency_key(request) -> str:
    key = request.headers.get(IDEMPOTENCY_KEY_HEADER, "").strip()
    if not key:
        raise ValidationError(
            "Idempotency-Key header is required for this mutation.",
            details={"header": IDEMPOTENCY_KEY_HEADER},
        )
    return key


def _actor_identifier(actor) -> str:
    if actor is None:
        return "anonymous"
    return str(getattr(actor, "pk", "anonymous"))


def _acquire_or_replay(
    *,
    scope: str,
    key: str,
    actor,
    request_fingerprint: str,
    ttl_seconds: int,
) -> tuple[IdempotencyKey, bool]:
    now = timezone.now()
    expires_at = now + timedelta(seconds=ttl_seconds)
    actor_identifier = _actor_identifier(actor)

    for _ in range(2):
        with transaction.atomic():
            record = (
                IdempotencyKey.objects.select_for_update()
                .filter(scope=scope, key=key, actor_identifier=actor_identifier)
                .first()
            )
            if record is None:
                try:
                    record = IdempotencyKey.objects.create(
                        scope=scope,
                        key=key,
                        actor=actor if getattr(actor, "is_authenticated", False) else None,
                        actor_identifier=actor_identifier,
                        request_fingerprint=request_fingerprint,
                        status=IdempotencyKey.STATUS_IN_PROGRESS,
                        expires_at=expires_at,
                    )
                    return record, False
                except IntegrityError:
                    continue

            if record.expires_at <= now:
                record.request_fingerprint = request_fingerprint
                record.status = IdempotencyKey.STATUS_IN_PROGRESS
                record.response_code = None
                record.response_payload = {}
                record.error_payload = {}
                record.expires_at = expires_at
                record.save(
                    update_fields=(
                        "request_fingerprint",
                        "status",
                        "response_code",
                        "response_payload",
                        "error_payload",
                        "expires_at",
                        "updated_at",
                        "last_seen_at",
                    )
                )
                return record, False

            if record.request_fingerprint != request_fingerprint:
                raise ConflictError(
                    "Idempotency key already used with a different request payload.",
                    details={"scope": scope},
                )

            if record.status == IdempotencyKey.STATUS_COMPLETED:
                return record, True

            if record.status == IdempotencyKey.STATUS_IN_PROGRESS:
                raise ConflictError(
                    "A request with the same idempotency key is still being processed.",
                    details={"scope": scope},
                )

            record.status = IdempotencyKey.STATUS_IN_PROGRESS
            record.response_code = None
            record.response_payload = {}
            record.error_payload = {}
            record.expires_at = expires_at
            record.save(
                update_fields=(
                    "status",
                    "response_code",
                    "response_payload",
                    "error_payload",
                    "expires_at",
                    "updated_at",
                    "last_seen_at",
                )
            )
            return record, False

    raise ConflictError("Could not acquire idempotency key lock.")


def _finalize_success(record: IdempotencyKey, *, payload: dict[str, Any], status_code: int) -> None:
    record.status = IdempotencyKey.STATUS_COMPLETED
    record.response_payload = payload
    record.response_code = status_code
    record.error_payload = {}
    record.save(
        update_fields=("status", "response_payload", "response_code", "error_payload", "updated_at", "last_seen_at")
    )


def _finalize_failure(record: IdempotencyKey, *, details: dict[str, Any]) -> None:
    record.status = IdempotencyKey.STATUS_FAILED
    record.error_payload = details
    record.save(update_fields=("status", "error_payload", "updated_at", "last_seen_at"))


def execute_idempotent_operation(
    *,
    scope: str,
    key: str,
    actor,
    method: str,
    path: str,
    body: dict[str, Any],
    execute: Callable[[], tuple[dict[str, Any], int]],
    ttl_seconds: int = DEFAULT_IDEMPOTENCY_TTL_SECONDS,
) -> IdempotencyResult:
    fingerprint = build_request_fingerprint(method=method, path=path, body=body)
    record, replayed = _acquire_or_replay(
        scope=scope,
        key=key,
        actor=actor,
        request_fingerprint=fingerprint,
        ttl_seconds=ttl_seconds,
    )
    if replayed:
        return IdempotencyResult(
            payload=record.response_payload,
            status_code=record.response_code or 200,
            replayed=True,
        )

    try:
        payload, status_code = execute()
    except Exception as exc:  # pragma: no cover - defensive rollback marker
        _finalize_failure(record, details={"error": str(exc)})
        raise

    _finalize_success(record, payload=payload, status_code=status_code)
    return IdempotencyResult(payload=payload, status_code=status_code, replayed=False)


def collect_idempotency_health_snapshot() -> dict[str, int]:
    now = timezone.now()
    aggregated = IdempotencyKey.objects.aggregate(
        in_progress_total=Count("id", filter=Q(status=IdempotencyKey.STATUS_IN_PROGRESS)),
        completed_total=Count("id", filter=Q(status=IdempotencyKey.STATUS_COMPLETED)),
        failed_total=Count("id", filter=Q(status=IdempotencyKey.STATUS_FAILED)),
        expired_total=Count("id", filter=Q(expires_at__lt=now)),
        oldest_in_progress_at=Min(
            "created_at",
            filter=Q(status=IdempotencyKey.STATUS_IN_PROGRESS),
        ),
    )
    oldest_in_progress_age_seconds = 0
    if aggregated["oldest_in_progress_at"] is not None:
        oldest_in_progress_age_seconds = int((now - aggregated["oldest_in_progress_at"]).total_seconds())

    return {
        "in_progress_total": aggregated["in_progress_total"] or 0,
        "completed_total": aggregated["completed_total"] or 0,
        "failed_total": aggregated["failed_total"] or 0,
        "expired_total": aggregated["expired_total"] or 0,
        "oldest_in_progress_age_seconds": oldest_in_progress_age_seconds,
    }


def cleanup_expired_idempotency_keys() -> int:
    retention_seconds = get_platform_settings().idempotency_retention_seconds
    cutoff = timezone.now() - timedelta(seconds=retention_seconds)
    return IdempotencyKey.objects.filter(expires_at__lt=cutoff).delete()[0]
