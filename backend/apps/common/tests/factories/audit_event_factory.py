import factory

from apps.common.models import AuditEvent
from apps.common.tests.factories.user_factory import UserFactory


class AuditEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditEvent

    actor = factory.SubFactory(UserFactory)
    action = factory.Sequence(lambda n: f"entity.updated.{n}")
    target_model = "accounts.User"
    target_id = factory.Sequence(lambda n: str(n + 1))
    metadata = factory.LazyFunction(dict)
