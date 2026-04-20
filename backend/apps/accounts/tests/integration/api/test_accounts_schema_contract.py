import pytest
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.django_db
def test_accounts_self_service_schema_tags_and_paths():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    me_path = "/api/accounts/v1/users/me/"
    me_tenants_path = "/api/accounts/v1/users/me/tenants/"
    favorites_path = "/api/accounts/v1/users/me/navigation-favorites/"
    deactivate_path = "/api/accounts/v1/users/me/deactivate/"

    assert me_path in paths
    assert me_tenants_path in paths
    assert favorites_path in paths
    assert deactivate_path in paths

    assert paths[me_path]["get"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[me_path]["patch"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[me_tenants_path]["get"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[favorites_path]["get"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[favorites_path]["put"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[deactivate_path]["post"]["tags"] == ["Accounts - User - Self Service"]

    me_schema_ref = paths[me_path]["get"]["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    component_name = me_schema_ref.rsplit("/", maxsplit=1)[-1]
    me_schema = schema["components"]["schemas"][component_name]
    assert "permissions" in me_schema["properties"]
    assert "feature_flags" in me_schema["properties"]
    assert "current_tenant_role" in me_schema["properties"]
