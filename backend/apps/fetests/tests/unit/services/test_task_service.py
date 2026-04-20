import pytest

from apps.common.models import AuditEvent
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory
from apps.common.exceptions import ValidationError
from apps.fetests.api.v1.services import create_task, update_task
from apps.fetests.models import Task
from apps.notification.models import Notification


@pytest.mark.django_db
def test_update_task_emits_notification_and_audit():
    actor = UserFactory()
    assignee = UserFactory()
    tenant = TenantFactory()
    TenantMembershipFactory(user=actor, tenant=tenant, is_active=True)
    TenantMembershipFactory(user=assignee, tenant=tenant, is_active=True)
    task = create_task(
        tenant=tenant,
        actor=actor,
        title="Implement filter panel",
        description="v1",
        assignee_id=assignee.pk,
        due_at=None,
        source="unit-test",
    )

    updated = update_task(
        task=task,
        tenant=tenant,
        actor=actor,
        title="Implement filter panel v2",
        description=None,
        due_at=None,
        source="unit-test",
    )

    assert updated.title == "Implement filter panel v2"
    assert Notification.objects.filter(
        tenant=tenant,
        recipient=assignee,
        metadata__event="task_updated",
        metadata__task_id=str(task.pk),
    ).exists()
    assert AuditEvent.objects.filter(
        action="fetests.task.updated",
        target_model="fetests.Task",
        target_id=str(task.pk),
    ).exists()


@pytest.mark.django_db
def test_create_task_requires_assignee_membership():
    actor = UserFactory()
    outsider = UserFactory()
    tenant = TenantFactory()
    TenantMembershipFactory(user=actor, tenant=tenant, is_active=True)

    with pytest.raises(ValidationError):
        create_task(
            tenant=tenant,
            actor=actor,
            title="Membership check",
            description="validation",
            assignee_id=outsider.pk,
            due_at=None,
            source="unit-test",
        )


@pytest.mark.django_db
def test_update_task_rejects_done_tasks():
    actor = UserFactory()
    tenant = TenantFactory()
    TenantMembershipFactory(user=actor, tenant=tenant, is_active=True)
    task = Task.objects.create(
        tenant=tenant,
        title="Closed item",
        description="done",
        status=Task.STATUS_DONE,
        created_by=actor,
        updated_by=actor,
    )

    with pytest.raises(ValidationError):
        update_task(
            task=task,
            tenant=tenant,
            actor=actor,
            title="Cannot change",
            description=None,
            due_at=None,
            source="unit-test",
        )
