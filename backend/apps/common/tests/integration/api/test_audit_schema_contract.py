import pytest
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.django_db
def test_audit_operations_schema_tags_and_paths():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    health_path = "/api/common/v1/audit-ops/health-snapshot/"
    verify_path = "/api/common/v1/audit-ops/verify-integrity/"
    export_path = "/api/common/v1/audit-ops/siem-export-preview/"
    archive_path = "/api/common/v1/audit-ops/archive-events/"
    setup_path = "/api/common/v1/audit-ops/setup-roles/"

    assert health_path in paths
    assert verify_path in paths
    assert export_path in paths
    assert archive_path in paths
    assert setup_path in paths

    assert paths[health_path]["get"]["tags"] == ["Common - Audit Operations - Monitoring"]
    assert paths[verify_path]["post"]["tags"] == ["Common - Audit Operations - Integrity"]
    assert paths[export_path]["get"]["tags"] == ["Common - Audit Operations - SIEM"]
    assert paths[archive_path]["post"]["tags"] == ["Common - Audit Operations - Retention"]
    assert paths[setup_path]["post"]["tags"] == ["Common - Audit Operations - Access"]
