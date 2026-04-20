from __future__ import annotations

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.common.api.v1.pagination import DefaultListPagination
from apps.common.api.v1.services import (
    ensure_user_in_tenant,
    extract_audit_correlation_ids,
    require_tenant,
    tenant_scoped_queryset,
)
from apps.fetests.api.v1.permissions import IsTaskUser
from apps.fetests.api.v1.schema import task_viewset_schema
from apps.fetests.api.v1.serializers import TaskAssignSerializer, TaskCreateSerializer, TaskReadSerializer, TaskUpdateSerializer
from apps.fetests.api.v1.services import assign_task, complete_task, create_task, list_tasks_for_tenant, update_task
from apps.fetests.models import Task


@task_viewset_schema
class TaskViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = Task.objects.none()
    permission_classes = [IsTaskUser]
    serializer_class = TaskReadSerializer
    pagination_class = DefaultListPagination

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Task.objects.none()
        tenant = require_tenant(self.request)
        ensure_user_in_tenant(user=self.request.user, tenant=tenant)
        return list_tasks_for_tenant(tenant=tenant)

    def get_serializer_class(self):
        if self.action == "create":
            return TaskCreateSerializer
        if self.action == "partial_update":
            return TaskUpdateSerializer
        if self.action == "assign":
            return TaskAssignSerializer
        return TaskReadSerializer

    def create(self, request, *args, **kwargs):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id, trace_id = extract_audit_correlation_ids(request)
        task = create_task(
            tenant=tenant,
            actor=request.user,
            title=serializer.validated_data["title"],
            description=serializer.validated_data.get("description", ""),
            assignee_id=serializer.validated_data.get("assignee_id"),
            due_at=serializer.validated_data.get("due_at"),
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(TaskReadSerializer(task).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        task = self.get_object()
        task = tenant_scoped_queryset(queryset=Task.objects.all(), tenant=tenant).get(pk=task.pk)
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        request_id, trace_id = extract_audit_correlation_ids(request)
        updated_task = update_task(
            task=task,
            tenant=tenant,
            actor=request.user,
            title=serializer.validated_data.get("title"),
            description=serializer.validated_data.get("description"),
            due_at=serializer.validated_data.get("due_at"),
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(TaskReadSerializer(updated_task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="assign")
    def assign(self, request, pk=None):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id, trace_id = extract_audit_correlation_ids(request)
        updated_task = assign_task(
            task=task,
            tenant=tenant,
            actor=request.user,
            assignee_id=serializer.validated_data["assignee_id"],
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(TaskReadSerializer(updated_task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        task = self.get_object()
        request_id, trace_id = extract_audit_correlation_ids(request)
        updated_task = complete_task(
            task=task,
            tenant=tenant,
            actor=request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(TaskReadSerializer(updated_task).data, status=status.HTTP_200_OK)
