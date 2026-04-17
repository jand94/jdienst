from rest_framework import mixins, status
from rest_framework.decorators import action
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.api.v1.permissions import IsSelfOrStaff, IsStaffUser
from apps.accounts.api.v1.schema import account_user_viewset_schema
from apps.accounts.api.v1.serializers import AccountUserReadSerializer, AccountUserUpdateSerializer
from apps.accounts.api.v1.services import deactivate_user, update_user_profile
from apps.accounts.api.v1.services import log_user_list_access, log_user_read_access
from apps.common.api.v1.services import (
    execute_idempotent_operation,
    extract_audit_correlation_ids,
    require_idempotency_key,
)
from apps.accounts.models import User


class AccountUserPagination(PageNumberPagination):
    page_size = 50
    max_page_size = 200
    page_size_query_param = "page_size"


@account_user_viewset_schema
class AccountUserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    queryset = User.objects.order_by("-date_joined", "-id")
    serializer_class = AccountUserReadSerializer
    pagination_class = AccountUserPagination

    def _execute_idempotent_update(
        self,
        *,
        request,
        scope: str,
        body: dict,
        execute,
    ) -> Response:
        key = require_idempotency_key(request)
        result = execute_idempotent_operation(
            scope=scope,
            key=key,
            actor=request.user,
            method=request.method,
            path=request.path,
            body=body,
            execute=execute,
        )
        response = Response(result.payload, status=result.status_code)
        if result.replayed:
            response["X-Idempotent-Replayed"] = "true"
        return response

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), IsStaffUser()]
        if self.action in {"retrieve", "partial_update", "update"}:
            return [IsAuthenticated(), IsSelfOrStaff()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "me":
            if getattr(self.request, "method", "").upper() == "PATCH":
                return AccountUserUpdateSerializer
            return AccountUserReadSerializer
        if self.action in {"partial_update", "update"}:
            return AccountUserUpdateSerializer
        return AccountUserReadSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_user_list_access(
            actor=request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return response

    def retrieve(self, request, *args, **kwargs):
        target = self.get_object()
        response = super().retrieve(request, *args, **kwargs)
        request_id, trace_id = extract_audit_correlation_ids(request)
        log_user_read_access(
            actor=request.user,
            target=target,
            source="api",
            scope="detail",
            request_id=request_id,
            trace_id=trace_id,
        )
        return response

    @action(detail=False, methods=["get", "patch"], url_path="me")
    @extend_schema(
        methods=["GET"],
        tags=["Accounts - User - Self Service"],
        summary="Retrieve authenticated user profile",
        responses=AccountUserReadSerializer,
    )
    @extend_schema(
        methods=["PATCH"],
        tags=["Accounts - User - Self Service"],
        summary="Partially update authenticated user profile",
        request=AccountUserUpdateSerializer,
        responses=AccountUserReadSerializer,
        parameters=[
            OpenApiParameter(
                name="Idempotency-Key",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Idempotency key for mutation safety.",
            )
        ],
    )
    def me(self, request):
        request_id, trace_id = extract_audit_correlation_ids(request)
        if request.method == "GET":
            serializer = AccountUserReadSerializer(request.user)
            log_user_read_access(
                actor=request.user,
                target=request.user,
                source="api",
                scope="self",
                request_id=request_id,
                trace_id=trace_id,
            )
            return Response(serializer.data)

        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return self._execute_idempotent_update(
            request=request,
            scope="accounts.user.me.patch",
            body=serializer.validated_data,
            execute=lambda: (
                AccountUserReadSerializer(
                    update_user_profile(
                        actor=request.user,
                        data=serializer.validated_data,
                        source="api",
                        request_id=request_id,
                        trace_id=trace_id,
                    )
                ).data,
                status.HTTP_200_OK,
            ),
        )

    @action(detail=False, methods=["post"], url_path="me/deactivate")
    @extend_schema(
        tags=["Accounts - User - Self Service"],
        summary="Deactivate authenticated user",
        request=None,
        responses=AccountUserReadSerializer,
        parameters=[
            OpenApiParameter(
                name="Idempotency-Key",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                required=True,
                description="Idempotency key for mutation safety.",
            )
        ],
    )
    def deactivate_me(self, request):
        request_id, trace_id = extract_audit_correlation_ids(request)
        return self._execute_idempotent_update(
            request=request,
            scope="accounts.user.me.deactivate",
            body={},
            execute=lambda: (
                AccountUserReadSerializer(
                    deactivate_user(
                        actor=request.user,
                        source="api",
                        request_id=request_id,
                        trace_id=trace_id,
                    )
                ).data,
                status.HTTP_200_OK,
            ),
        )

    def partial_update(self, request, *args, **kwargs):
        target = self.get_object()
        request_id, trace_id = extract_audit_correlation_ids(request)
        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return self._execute_idempotent_update(
            request=request,
            scope="accounts.user.partial_update",
            body=serializer.validated_data,
            execute=lambda: (
                AccountUserReadSerializer(
                    update_user_profile(
                        actor=target,
                        data=serializer.validated_data,
                        source="api",
                        request_id=request_id,
                        trace_id=trace_id,
                    )
                ).data,
                status.HTTP_200_OK,
            ),
        )

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        request_id, trace_id = extract_audit_correlation_ids(request)
        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=False,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        return self._execute_idempotent_update(
            request=request,
            scope="accounts.user.update",
            body=serializer.validated_data,
            execute=lambda: (
                AccountUserReadSerializer(
                    update_user_profile(
                        actor=target,
                        data=serializer.validated_data,
                        source="api",
                        request_id=request_id,
                        trace_id=trace_id,
                    )
                ).data,
                status.HTTP_200_OK,
            ),
        )
