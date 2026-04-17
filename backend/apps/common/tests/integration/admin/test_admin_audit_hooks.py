import pytest
from django.contrib import admin
from django.test import RequestFactory

from apps.accounts.models import User
from apps.common.models import AuditEvent
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_user_admin_create_update_delete_generate_audit_events():
    admin_user = UserFactory(is_staff=True, is_superuser=True)
    request_factory = RequestFactory()
    user_admin = admin.site._registry[User]

    create_request = request_factory.post("/admin/accounts/user/add/")
    create_request.user = admin_user
    create_request.META["REMOTE_ADDR"] = "127.0.0.1"
    create_request.META["HTTP_USER_AGENT"] = "pytest-admin"

    created_user = User(username="audited_user", email="audited@example.com")
    user_admin.save_model(create_request, created_user, form=None, change=False)

    create_event = AuditEvent.objects.filter(
        action="admin.create",
        target_model="accounts.User",
        target_id=str(created_user.pk),
    ).first()
    assert create_event is not None
    assert create_event.actor_id == admin_user.id

    created_user.first_name = "Changed"
    update_request = request_factory.post("/admin/accounts/user/change/")
    update_request.user = admin_user
    update_request.META["REMOTE_ADDR"] = "127.0.0.1"
    update_request.META["HTTP_USER_AGENT"] = "pytest-admin"
    user_admin.save_model(update_request, created_user, form=None, change=True)

    update_event = AuditEvent.objects.filter(
        action="admin.update",
        target_model="accounts.User",
        target_id=str(created_user.pk),
    ).first()
    assert update_event is not None
    assert update_event.metadata.get("source") == "django-admin"
    assert update_event.metadata.get("changes", {}).get("first_name") == {
        "old": "",
        "new": "Changed",
    }

    delete_request = request_factory.post("/admin/accounts/user/delete/")
    delete_request.user = admin_user
    delete_request.META["REMOTE_ADDR"] = "127.0.0.1"
    delete_request.META["HTTP_USER_AGENT"] = "pytest-admin"
    deleted_target_id = str(created_user.pk)
    user_admin.delete_model(delete_request, created_user)

    delete_event = AuditEvent.objects.filter(
        action="admin.delete",
        target_model="accounts.User",
        target_id=deleted_target_id,
    ).first()
    assert delete_event is not None
    assert delete_event.actor_id == admin_user.id
