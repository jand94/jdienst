import pytest
from django.conf import settings
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.django_db
def test_auth_schema_contains_jwt_endpoints_and_bearer_security():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    assert "/api/auth/v1/login/" in paths
    assert "/api/auth/v1/refresh/" in paths
    assert "/api/auth/v1/logout/" in paths

    security_schemes = schema["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert security_schemes["BearerAuth"]["type"] == "http"
    assert security_schemes["BearerAuth"]["scheme"] == "bearer"

    assert paths["/api/auth/v1/logout/"]["post"]["security"] == [{"BearerAuth": []}]
    refresh_cookie_parameter = paths["/api/auth/v1/refresh/"]["post"]["parameters"][0]
    assert refresh_cookie_parameter["name"] == settings.AUTH_REFRESH_COOKIE_NAME
    assert paths["/api/auth/v1/logout/"]["post"]["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ].endswith("/AuthLogoutResponse")
