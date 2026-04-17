import pytest
from django.contrib.auth.models import Group, Permission

from apps.common.api.v1.services import is_audit_operator, is_audit_reader
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


@pytest.mark.django_db
def test_is_audit_operator_requires_explicit_operate_permission():
    user = UserFactory(is_staff=True)
    user.user_permissions.add(Permission.objects.get(codename="view_auditevent"))

    assert is_audit_operator(user) is False


@pytest.mark.django_db
def test_is_audit_operator_accepts_group_membership():
    user = UserFactory(is_staff=True)
    role = Group.objects.create(name="AuditOperator")
    role.permissions.add(Permission.objects.get(codename="operate_auditevent"))
    user.groups.add(role)

    assert is_audit_operator(user) is True
