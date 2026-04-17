from importlib import import_module

import pytest


@pytest.mark.django_db
def test_common_user_factory_creates_user():
    from apps.common.tests.factories import UserFactory

    user = UserFactory()

    assert user.pk is not None


def test_root_urls_module_loads_with_api_includes():
    urls_module = import_module("backend.urls")
    routes = [str(pattern.pattern) for pattern in urls_module.urlpatterns]

    assert "api/accounts/" in routes
    assert "api/common/" in routes
