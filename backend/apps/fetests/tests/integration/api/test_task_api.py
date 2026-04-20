import pytest
from django.urls import reverse

from apps.common.models import AuditEvent
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory, UserFactory
from apps.fetests.models import Task
from apps.notification.models import Notification


@pytest.mark.django_db
def test_create_task_with_assignee_creates_notification_and_audit(api_client):
    actor = UserFactory()
    assignee = UserFactory()
    tenant = TenantFactory(slug="tenant-fe")
    TenantMembershipFactory(user=actor, tenant=tenant, is_active=True)
    TenantMembershipFactory(user=assignee, tenant=tenant, is_active=True)
    api_client.force_authenticate(user=actor)

    response = api_client.post(
        reverse("fetests-task-list"),
        data={
            "title": "Frontend QA Ticket",
            "description": "Test flow for assignment",
            "assignee_id": assignee.pk,
        },
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )

    assert response.status_code == 201
    task_id = response.data["id"]
    task = Task.objects.get(pk=task_id)
    assert task.assignee_id == assignee.pk
    assert Notification.objects.filter(
        tenant=tenant,
        recipient=assignee,
        metadata__event="task_created_with_assignment",
        metadata__task_id=str(task.pk),
    ).exists()
    assert AuditEvent.objects.filter(
        action="fetests.task.created",
        target_model="fetests.Task",
        target_id=str(task.pk),
    ).exists()


@pytest.mark.django_db
def test_assign_and_complete_task_send_notifications(api_client):
    actor = UserFactory()
    assignee = UserFactory()
    tenant = TenantFactory(slug="tenant-flow")
    TenantMembershipFactory(user=actor, tenant=tenant, is_active=True)
    TenantMembershipFactory(user=assignee, tenant=tenant, is_active=True)
    task = Task.objects.create(
        tenant=tenant,
        title="Implement UI task board",
        description="Initial open task",
        status=Task.STATUS_OPEN,
        created_by=actor,
        updated_by=actor,
    )
    api_client.force_authenticate(user=actor)

    assign_response = api_client.post(
        reverse("fetests-task-assign", kwargs={"pk": task.pk}),
        data={"assignee_id": assignee.pk},
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )
    assert assign_response.status_code == 200
    task.refresh_from_db()
    assert task.assignee_id == assignee.pk
    assert task.status == Task.STATUS_IN_PROGRESS

    complete_response = api_client.post(
        reverse("fetests-task-complete", kwargs={"pk": task.pk}),
        data={},
        format="json",
        HTTP_X_TENANT_SLUG=tenant.slug,
    )
    assert complete_response.status_code == 200
    task.refresh_from_db()
    assert task.status == Task.STATUS_DONE
    assert Notification.objects.filter(
        tenant=tenant,
        metadata__event="task_completed",
        metadata__task_id=str(task.pk),
    ).exists()
    assert AuditEvent.objects.filter(
        action="fetests.task.completed",
        target_model="fetests.Task",
        target_id=str(task.pk),
    ).exists()
