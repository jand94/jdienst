import pytest
from django.contrib.auth.models import Group, Permission

from apps.common.api.v1.services import is_audit_reader
from apps.common.tests.factories import UserFactory


@pytest.mark.django_db
def test_is_audit_reader_accepts_direct_permission():
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="view_auditevent"))

    assert is_audit_reader(user) is True


@pytest.mark.django_db
def test_is_audit_reader_accepts_group_permission():
    user = UserFactory(is_staff=True)
    role = Group.objects.create(name="AuditReader")
    role.permissions.add(Permission.objects.get(codename="view_auditevent"))
    user.groups.add(role)

    assert is_audit_reader(user) is True
