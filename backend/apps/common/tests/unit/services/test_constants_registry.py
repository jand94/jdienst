from apps.common.constants import ErrorCode, HeaderName


def test_error_codes_are_stable_strings():
    assert ErrorCode.VALIDATION_ERROR == "validation_error"
    assert ErrorCode.INTERNAL_ERROR == "internal_error"


def test_header_names_are_stable_strings():
    assert HeaderName.IDEMPOTENCY_KEY == "Idempotency-Key"
    assert HeaderName.TENANT_SLUG == "X-Tenant-Slug"
