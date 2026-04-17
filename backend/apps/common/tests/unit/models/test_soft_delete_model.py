import pytest

from apps.common.models import Tenant
from apps.common.tests.factories import TenantFactory, UserFactory


@pytest.mark.django_db
def test_soft_delete_model_hides_deleted_items_from_default_manager():
    tenant = TenantFactory()
    tenant.soft_delete()

    assert Tenant.objects.filter(pk=tenant.pk).exists() is False
    assert Tenant.all_objects.filter(pk=tenant.pk).exists() is True
    assert Tenant.deleted_objects.filter(pk=tenant.pk).exists() is True


@pytest.mark.django_db
def test_soft_delete_and_restore_track_actor():
    tenant = TenantFactory()
    actor = UserFactory()

    tenant.soft_delete(actor=actor, reason="cleanup")
    tenant.refresh_from_db()
    assert tenant.deleted_by_id == actor.id
    assert tenant.delete_reason == "cleanup"

    tenant.restore()
    tenant.refresh_from_db()
    assert tenant.deleted_at is None
    assert tenant.deleted_by is None
