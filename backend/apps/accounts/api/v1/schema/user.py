from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.accounts.api.v1.serializers import (
    AccountUserReadSerializer,
    AccountUserTenantMembershipSerializer,
    AccountUserUpdateSerializer,
)
from apps.common.api.v1.schema import idempotency_key_header_parameter, tenant_slug_header_parameter


account_user_viewset_schema = extend_schema_view(
    list=extend_schema(
        tags=["Accounts - User"],
        summary="List users (staff only)",
        parameters=[
            tenant_slug_header_parameter(required=True)
        ],
    ),
    retrieve=extend_schema(
        tags=["Accounts - User"],
        summary="Retrieve user profile by id",
        parameters=[
            tenant_slug_header_parameter(required=True)
        ],
    ),
    update=extend_schema(
        tags=["Accounts - User"],
        summary="Update user profile by id",
        request=AccountUserUpdateSerializer,
        responses=AccountUserReadSerializer,
        parameters=[
            tenant_slug_header_parameter(required=True),
            idempotency_key_header_parameter(required=True),
        ],
    ),
    partial_update=extend_schema(
        tags=["Accounts - User"],
        summary="Partially update user profile by id",
        request=AccountUserUpdateSerializer,
        responses=AccountUserReadSerializer,
        parameters=[
            tenant_slug_header_parameter(required=True),
            idempotency_key_header_parameter(required=True),
        ],
    ),
    me_tenants=extend_schema(
        tags=["Accounts - User - Self Service"],
        summary="List active tenant memberships for authenticated user",
        responses=AccountUserTenantMembershipSerializer(many=True),
    ),
)
