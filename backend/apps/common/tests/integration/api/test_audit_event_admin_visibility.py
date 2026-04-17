import pytest
from django.urls import reverse

from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_admin_audit_event_changelist_is_visible_for_superuser(client):
    admin_user = UserFactory(is_staff=True, is_superuser=True)
    AuditEvent.objects.create(
        actor=admin_user,
        action="admin.login",
        target_model="accounts.User",
        target_id=str(admin_user.pk),
        metadata={"source": "integration-test"},
    )

    client.force_login(admin_user)
    response = client.get(reverse("admin:common_auditevent_changelist"))

    assert response.status_code == 200
    assert b"admin.login" in response.content
