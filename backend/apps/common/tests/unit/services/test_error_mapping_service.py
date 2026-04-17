from types import SimpleNamespace

from apps.common.api.v1.services.error_mapping_service import map_exception_to_response
from apps.common.exceptions import ConflictError


def test_map_exception_to_response_handles_common_error():
    request = SimpleNamespace(headers={"X-Request-ID": "req-1", "X-Trace-ID": "trace-1"})

    status_code, payload = map_exception_to_response(
        ConflictError("Already processed"),
        request=request,
    )

    assert status_code == 409
    assert payload["code"] == "conflict_error"
    assert payload["message"] == "Already processed"
    assert payload["request_id"] == "req-1"
    assert payload["trace_id"] == "trace-1"
