from drf_spectacular.utils import extend_schema, extend_schema_view

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
    ),
    partial_update=extend_schema(
        tags=["Accounts - User"],
        summary="Partially update user profile by id",
        request=AccountUserUpdateSerializer,
        responses=AccountUserReadSerializer,
    ),
)
