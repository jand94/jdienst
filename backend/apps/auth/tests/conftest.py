import pytest
from rest_framework.test import APIClient
from apps.common.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()
