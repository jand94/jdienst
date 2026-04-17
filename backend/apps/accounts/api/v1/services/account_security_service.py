from apps.common.api.v1.services import record_audit_event


def log_auth_attempt(
    *,
    actor=None,
    success: bool,
    source: str,
    metadata: dict | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
):
    action = "auth.login.succeeded" if success else "auth.login.failed"
    target_id = str(getattr(actor, "pk", "unknown"))
    audit_metadata = {"source": source, "result": "succeeded" if success else "failed"}
    if metadata:
        audit_metadata.update(metadata)

    return record_audit_event(
        action=action,
        target_model="accounts.User",
        target_id=target_id,
        actor=actor,
        metadata=audit_metadata,
        request_id=request_id,
        trace_id=trace_id,
    )


def log_permission_denied(
    *,
    actor=None,
    resource: str,
    source: str,
    metadata: dict | None = None,
    request_id: str | None = None,
    trace_id: str | None = None,
):
    target_id = str(getattr(actor, "pk", "unknown"))
    audit_metadata = {
        "source": source,
        "resource": resource,
    }
    if metadata:
        audit_metadata.update(metadata)

    return record_audit_event(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id=target_id,
        actor=actor,
        metadata=audit_metadata,
        request_id=request_id,
        trace_id=trace_id,
    )
