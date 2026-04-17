import factory

from apps.common.models import Tenant


class TenantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tenant
        django_get_or_create = ("slug",)

    slug = factory.Sequence(lambda n: f"tenant-{n}")
    name = factory.LazyAttribute(lambda obj: obj.slug.title())
    status = Tenant.STATUS_ACTIVE
