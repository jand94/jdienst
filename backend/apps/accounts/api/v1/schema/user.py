from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view

from apps.accounts.api.v1.serializers import AccountUserReadSerializer, AccountUserUpdateSerializer


account_user_viewset_schema = extend_schema_view(
    list=extend_schema(
        tags=["Accounts - User"],
        summary="List users (staff only)",
    ),
    retrieve=extend_schema(
        tags=["Accounts - User"],
        summary="Retrieve user profile by id",
    ),
    update=extend_schema(
        tags=["Accounts - User"],
        summary="Update user profile by id",
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
    ),
    partial_update=extend_schema(
        tags=["Accounts - User"],
        summary="Partially update user profile by id",
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
    ),
)
