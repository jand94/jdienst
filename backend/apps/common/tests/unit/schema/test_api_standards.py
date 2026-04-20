from apps.common.api.v1.pagination import DefaultListPagination, DefaultStreamPagination
from apps.common.api.v1.schema.headers import (
    idempotency_key_header_parameter,
    tenant_slug_header_parameter,
)


def test_default_list_pagination_contract():
    assert DefaultListPagination.page_size == 50
    assert DefaultListPagination.max_page_size == 200
    assert DefaultListPagination.page_size_query_param == "page_size"


def test_default_stream_pagination_contract():
    assert DefaultStreamPagination.page_size == 20
    assert DefaultStreamPagination.max_page_size == 100
    assert DefaultStreamPagination.page_size_query_param == "page_size"


def test_header_parameter_helpers_use_common_constants():
    tenant_header = tenant_slug_header_parameter(required=True)
    idempotency_header = idempotency_key_header_parameter(required=True)

    assert tenant_header.name == "X-Tenant-Slug"
    assert tenant_header.required is True
    assert idempotency_header.name == "Idempotency-Key"
    assert idempotency_header.required is True
