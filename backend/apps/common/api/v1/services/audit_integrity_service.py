from __future__ import annotations

import hashlib
import hmac

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.common.api.v1.services.audit_service import _calculate_integrity_hash, record_audit_event
from apps.common.models import AuditEvent, AuditIntegrityCheckpoint, AuditIntegrityVerification


def _sign_hash(anchor_hash: str) -> str:
    key = getattr(settings, "AUDIT_INTEGRITY_SIGNING_KEY", settings.SECRET_KEY)
    digest = hmac.new(key.encode("utf-8"), anchor_hash.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def create_integrity_checkpoint(*, metadata: dict | None = None) -> AuditIntegrityCheckpoint:
    latest_event = AuditEvent.objects.order_by("-created_at", "-id").first()
    if latest_event is None:
        raise ValueError("Cannot create integrity checkpoint without audit events.")

    latest_checkpoint = AuditIntegrityCheckpoint.objects.order_by("-sequence").first()
    sequence = (latest_checkpoint.sequence + 1) if latest_checkpoint else 1
    checkpoint = AuditIntegrityCheckpoint.objects.create(
        sequence=sequence,
        anchor_event=latest_event,
        anchor_hash=latest_event.integrity_hash,
        signature=_sign_hash(latest_event.integrity_hash),
        metadata=metadata or {},
        verified_at=timezone.now(),
    )
    return checkpoint


def _verify_chain(*, events: list[AuditEvent], initial_previous_hash: str = "") -> tuple[bool, dict]:
    previous_hash = initial_previous_hash
    checked_events = 0
    mismatch: dict | None = None

    for event in events:
        expected_integrity_hash = _calculate_integrity_hash(
            action=event.action,
            target_model=event.target_model,
            target_id=event.target_id,
            actor_id=event.actor_id,
            metadata=event.metadata,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            previous_hash=previous_hash,
        )
        checked_events += 1
        if event.previous_hash != previous_hash:
            mismatch = {
                "reason": "previous_hash_mismatch",
                "event_id": str(event.pk),
                "expected_previous_hash": previous_hash,
                "actual_previous_hash": event.previous_hash,
            }
            break
        if event.integrity_hash != expected_integrity_hash:
            mismatch = {
                "reason": "integrity_hash_mismatch",
                "event_id": str(event.pk),
                "expected_integrity_hash": expected_integrity_hash,
                "actual_integrity_hash": event.integrity_hash,
            }
            break
        previous_hash = event.integrity_hash

    details = {
        "checked_events": checked_events,
        "last_hash": previous_hash,
    }
    if mismatch:
        details["mismatch"] = mismatch
        return False, details
    return True, details


def verify_integrity_chain(
    *,
    limit: int | None = None,
    create_checkpoint: bool = False,
    source: str = "system",
) -> AuditIntegrityVerification:
    queryset = AuditEvent.objects.order_by("created_at", "id")
    if limit:
        event_ids = list(queryset.values_list("id", flat=True))
        event_ids = event_ids[-limit:]
        queryset = queryset.filter(id__in=event_ids).order_by("created_at", "id")
    events = list(queryset)

    initial_previous_hash = events[0].previous_hash if limit and events else ""
    is_valid, details = _verify_chain(
        events=events,
        initial_previous_hash=initial_previous_hash,
    )
    checkpoint = None
    with transaction.atomic():
        if is_valid and create_checkpoint and events:
            checkpoint = create_integrity_checkpoint(
                metadata={
                    "source": source,
                    "checked_events": details["checked_events"],
                }
            )

        verification = AuditIntegrityVerification.objects.create(
            status=(
                AuditIntegrityVerification.STATUS_PASSED
                if is_valid
                else AuditIntegrityVerification.STATUS_FAILED
            ),
            checked_events=details["checked_events"],
            last_event_hash=details["last_hash"],
            details=details,
            checkpoint=checkpoint,
            finished_at=timezone.now(),
        )

        record_audit_event(
            action="common.audit_integrity.verified",
            target_model="common.AuditIntegrityVerification",
            target_id=str(verification.pk),
            metadata={
                "source": source,
                "status": verification.status,
                "checked_events": verification.checked_events,
            },
        )

    latest_checkpoint = AuditIntegrityCheckpoint.objects.order_by("-sequence").first()
    if latest_checkpoint:
        expected_signature = _sign_hash(latest_checkpoint.anchor_hash)
        if latest_checkpoint.signature != expected_signature:
            verification.status = AuditIntegrityVerification.STATUS_FAILED
            details["checkpoint_mismatch"] = {
                "checkpoint_id": str(latest_checkpoint.pk),
                "expected_signature": expected_signature,
                "actual_signature": latest_checkpoint.signature,
            }
            verification.details = details
            verification.save(update_fields=("status", "details", "updated_at"))

    return verification
