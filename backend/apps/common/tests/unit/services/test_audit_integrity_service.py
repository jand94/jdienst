import pytest

from apps.common.api.v1.services import (
    backfill_integrity_hashes,
    create_integrity_checkpoint,
    verify_integrity_chain,
)
from apps.common.api.v1.services.audit_service import record_audit_event
from apps.common.models import AuditEvent, AuditIntegrityVerification


@pytest.mark.django_db
def test_verify_integrity_chain_creates_checkpoint_when_requested():
    record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    record_audit_event(
        action="accounts.user.updated",
        target_model="accounts.User",
        target_id="2",
        metadata={"source": "api"},
    )

    verification = verify_integrity_chain(create_checkpoint=True, source="unit-test")

    assert verification.status == AuditIntegrityVerification.STATUS_PASSED
    assert verification.checked_events >= 2
    assert verification.checkpoint is not None
    assert verification.checkpoint.signature


@pytest.mark.django_db
def test_verify_integrity_chain_detects_hash_tampering():
    event = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=event.pk).update(integrity_hash="broken")

    verification = verify_integrity_chain(source="unit-test")

    assert verification.status == AuditIntegrityVerification.STATUS_FAILED
    assert verification.details["mismatch"]["reason"] == "integrity_hash_mismatch"


@pytest.mark.django_db
def test_create_integrity_checkpoint_requires_existing_events():
    with pytest.raises(ValueError):
        create_integrity_checkpoint()


@pytest.mark.django_db
def test_backfill_integrity_hashes_dry_run_reports_without_writing():
    event = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="20",
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=event.pk).update(previous_hash="", integrity_hash="")

    result = backfill_integrity_hashes(dry_run=True, source="unit-test")
    event.refresh_from_db()

    assert result["checked_events"] >= 1
    assert result["corrected_events"] >= 1
    assert event.integrity_hash == ""


@pytest.mark.django_db
def test_backfill_integrity_hashes_repairs_chain_and_verifies():
    first = record_audit_event(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    second = record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="2",
        metadata={"source": "api"},
    )
    AuditEvent.objects.filter(pk=first.pk).update(integrity_hash="")
    AuditEvent.objects.filter(pk=second.pk).update(previous_hash="", integrity_hash="")

    result = backfill_integrity_hashes(source="unit-test")
    verification = verify_integrity_chain(source="unit-test")
    first.refresh_from_db()
    second.refresh_from_db()

    assert result["corrected_events"] >= 2
    assert first.integrity_hash != ""
    assert second.previous_hash == first.integrity_hash
    assert verification.status == AuditIntegrityVerification.STATUS_PASSED
