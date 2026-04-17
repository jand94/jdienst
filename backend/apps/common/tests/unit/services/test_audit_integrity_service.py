import pytest

from apps.common.api.v1.services import create_integrity_checkpoint, verify_integrity_chain
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
