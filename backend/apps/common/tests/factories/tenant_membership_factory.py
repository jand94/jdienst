import factory

from apps.common.models import TenantMembership
from apps.common.tests.factories.tenant_factory import TenantFactory
from apps.common.tests.factories.user_factory import UserFactory


class TenantMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TenantMembership

    tenant = factory.SubFactory(TenantFactory)
    user = factory.SubFactory(UserFactory)
    role = TenantMembership.ROLE_MEMBER
    is_active = True
