import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_audit_event_api_requires_audit_reader_permission():
    user = UserFactory(is_staff=True)
    event = AuditEvent.objects.create(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id=str(user.pk),
        metadata={"source": "api"},
    )

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("common-audit-event-list")
    response = client.get(url)

    assert response.status_code == 403
    assert event.pk is not None


@pytest.mark.django_db
def test_audit_event_api_lists_and_filters_for_auditor_role():
    auditor = UserFactory(is_staff=True)
    view_perm = Permission.objects.get(codename="view_auditevent")
    auditor.user_permissions.add(view_perm)

    AuditEvent.objects.create(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id="1",
        metadata={"source": "api"},
    )
    matching = AuditEvent.objects.create(
        action="security.permission.denied",
        target_model="accounts.User",
        target_id="2",
        metadata={"source": "api"},
    )

    client = APIClient()
    client.force_authenticate(user=auditor)
    url = reverse("common-audit-event-list")
    response = client.get(url, {"action": "security.permission.denied"})

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["id"] == str(matching.pk)
