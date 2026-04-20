import pytest
from rest_framework.test import APIClient
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True)


@pytest.fixture
def tenant():
    return TenantFactory()


@pytest.fixture
def tenant_membership(user, tenant):
    return TenantMembershipFactory(user=user, tenant=tenant, is_active=True)


@pytest.fixture
def staff_tenant_membership(staff_user, tenant):
    return TenantMembershipFactory(user=staff_user, tenant=tenant, is_active=True)
