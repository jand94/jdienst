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


@pytest.mark.django_db
def test_platform_schema_tags_and_paths():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    snapshot_path = "/api/common/v1/platform-health/snapshot/"
    check_path = "/api/common/v1/platform-ops/check/"
    slo_path = "/api/common/v1/platform-ops/slo-report/"
    tenant_consistency_path = "/api/common/v1/platform-ops/tenant-consistency/"
    soft_delete_cleanup_path = "/api/common/v1/platform-ops/soft-delete-cleanup/"

    assert snapshot_path in paths
    assert check_path in paths
    assert slo_path in paths
    assert tenant_consistency_path in paths
    assert soft_delete_cleanup_path in paths

    assert paths[snapshot_path]["get"]["tags"] == ["Common - Platform - Health"]
    assert paths[check_path]["post"]["tags"] == ["Common - Platform - Operations"]
    assert paths[slo_path]["post"]["tags"] == ["Common - Platform - Operations"]
    assert paths[tenant_consistency_path]["post"]["tags"] == ["Common - Platform - Operations"]
    assert paths[soft_delete_cleanup_path]["post"]["tags"] == ["Common - Platform - Operations"]
