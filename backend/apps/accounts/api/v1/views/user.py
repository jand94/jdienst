from rest_framework import mixins, status
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.accounts.api.v1.permissions import IsSelfOrStaff, IsStaffUser
from apps.accounts.api.v1.schema import account_user_viewset_schema
from apps.accounts.api.v1.serializers import AccountUserReadSerializer, AccountUserUpdateSerializer
from apps.accounts.api.v1.services import deactivate_user, update_user_profile
from apps.accounts.api.v1.services import log_user_list_access, log_user_read_access
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
        log_user_list_access(actor=request.user, source="api")
        return response

    def retrieve(self, request, *args, **kwargs):
        target = self.get_object()
        response = super().retrieve(request, *args, **kwargs)
        log_user_read_access(actor=request.user, target=target, source="api", scope="detail")
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
    )
    def me(self, request):
        if request.method == "GET":
            serializer = AccountUserReadSerializer(request.user)
            log_user_read_access(
                actor=request.user,
                target=request.user,
                source="api",
                scope="self",
            )
            return Response(serializer.data)

        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = update_user_profile(
            actor=request.user,
            data=serializer.validated_data,
            source="api",
        )
        return Response(AccountUserReadSerializer(user).data)

    @action(detail=False, methods=["post"], url_path="me/deactivate")
    @extend_schema(
        tags=["Accounts - User - Self Service"],
        summary="Deactivate authenticated user",
        request=None,
        responses=AccountUserReadSerializer,
    )
    def deactivate_me(self, request):
        user = deactivate_user(actor=request.user, source="api")
        return Response(AccountUserReadSerializer(user).data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        target = self.get_object()
        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = update_user_profile(
            actor=target,
            data=serializer.validated_data,
            source="api",
        )
        return Response(AccountUserReadSerializer(updated).data)

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        serializer = AccountUserUpdateSerializer(
            data=request.data,
            partial=False,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        updated = update_user_profile(
            actor=target,
            data=serializer.validated_data,
            source="api",
        )
        return Response(AccountUserReadSerializer(updated).data)
