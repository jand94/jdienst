from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view

from apps.common.api.v1.schema import tenant_slug_header_parameter
from apps.fetests.api.v1.serializers import TaskAssignSerializer, TaskCreateSerializer, TaskReadSerializer, TaskUpdateSerializer


task_viewset_schema = extend_schema_view(
    list=extend_schema(
        operation_id="fetests_v1_tasks_list",
        tags=["FE Tests - Tasks"],
        summary="List tenant scoped tasks for frontend testing",
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={200: TaskReadSerializer(many=True), 403: OpenApiResponse(description="Forbidden.")},
    ),
    create=extend_schema(
        operation_id="fetests_v1_tasks_create",
        tags=["FE Tests - Tasks"],
        summary="Create a task and optionally assign it",
        request=TaskCreateSerializer,
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={201: TaskReadSerializer, 400: OpenApiResponse(description="Validation error.")},
    ),
    partial_update=extend_schema(
        operation_id="fetests_v1_tasks_partial_update",
        tags=["FE Tests - Tasks"],
        summary="Update task fields and notify involved users",
        request=TaskUpdateSerializer,
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={200: TaskReadSerializer, 400: OpenApiResponse(description="Validation error.")},
    ),
    retrieve=extend_schema(
        operation_id="fetests_v1_tasks_retrieve",
        tags=["FE Tests - Tasks"],
        summary="Retrieve one task",
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={200: TaskReadSerializer, 404: OpenApiResponse(description="Not found.")},
    ),
    assign=extend_schema(
        operation_id="fetests_v1_tasks_assign_create",
        tags=["FE Tests - Tasks - Assignment"],
        summary="Assign task to a tenant member",
        request=TaskAssignSerializer,
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={200: TaskReadSerializer, 400: OpenApiResponse(description="Validation error.")},
    ),
    complete=extend_schema(
        operation_id="fetests_v1_tasks_complete_create",
        tags=["FE Tests - Tasks - State"],
        summary="Mark task as completed",
        request=None,
        parameters=[tenant_slug_header_parameter(required=True)],
        responses={200: TaskReadSerializer, 400: OpenApiResponse(description="Validation error.")},
    ),
)
