import pytest
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.django_db
def test_accounts_self_service_schema_tags_and_paths():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    me_path = "/api/accounts/v1/users/me/"
    deactivate_path = "/api/accounts/v1/users/me/deactivate/"

    assert me_path in paths
    assert deactivate_path in paths

    assert paths[me_path]["get"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[me_path]["patch"]["tags"] == ["Accounts - User - Self Service"]
    assert paths[deactivate_path]["post"]["tags"] == ["Accounts - User - Self Service"]
