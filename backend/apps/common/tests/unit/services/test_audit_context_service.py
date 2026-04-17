from types import SimpleNamespace

from apps.common.api.v1.services.audit_context_service import extract_audit_correlation_ids


def test_extract_audit_correlation_ids_prefers_request_and_trace_headers():
    request = SimpleNamespace(
        headers={
            "X-Request-ID": "req-1",
            "X-Trace-ID": "trace-1",
            "traceparent": "00-abc-123-01",
        }
    )

    request_id, trace_id = extract_audit_correlation_ids(request)

    assert request_id == "req-1"
    assert trace_id == "trace-1"


def test_extract_audit_correlation_ids_falls_back_to_traceparent():
    request = SimpleNamespace(
        headers={
            "X-Correlation-ID": "corr-2",
            "traceparent": "00-xyz-987-01",
        }
    )

    request_id, trace_id = extract_audit_correlation_ids(request)

    assert request_id == "corr-2"
    assert trace_id == "00-xyz-987-01"
