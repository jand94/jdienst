from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.common.api.v1.serializers import (
    ApiErrorResponseSerializer,
    TenantMembershipSerializer,
    TenantSerializer,
    TenantStatusUpdateSerializer,
)


tenant_ops_viewset_schema = extend_schema_view(
    list=extend_schema(
        operation_id="common_v1_tenants_list",
        tags=["Common - Tenant Operations"],
        summary="List tenants for platform operations.",
        responses={200: TenantSerializer(many=True), 403: ApiErrorResponseSerializer},
    ),
    create=extend_schema(
        operation_id="common_v1_tenants_create",
        tags=["Common - Tenant Operations"],
        summary="Create tenant.",
        request=TenantSerializer,
        responses={201: TenantSerializer, 403: ApiErrorResponseSerializer},
    ),
    retrieve=extend_schema(
        operation_id="common_v1_tenants_retrieve",
        tags=["Common - Tenant Operations"],
        summary="Retrieve tenant.",
        responses={200: TenantSerializer, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
    update=extend_schema(
        operation_id="common_v1_tenants_update",
        tags=["Common - Tenant Operations"],
        summary="Update tenant.",
        request=TenantSerializer,
        responses={200: TenantSerializer, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
    partial_update=extend_schema(
        operation_id="common_v1_tenants_partial_update",
        tags=["Common - Tenant Operations"],
        summary="Partially update tenant.",
        request=TenantSerializer,
        responses={200: TenantSerializer, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
    destroy=extend_schema(
        operation_id="common_v1_tenants_destroy",
        tags=["Common - Tenant Operations"],
        summary="Soft-delete tenant.",
        responses={204: None, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
    set_status=extend_schema(
        operation_id="common_v1_tenants_set_status",
        tags=["Common - Tenant Operations"],
        summary="Set tenant status.",
        request=TenantStatusUpdateSerializer,
        responses={200: TenantSerializer, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
)


tenant_membership_ops_viewset_schema = extend_schema_view(
    list=extend_schema(
        operation_id="common_v1_tenant_memberships_list",
        tags=["Common - Tenant Membership Operations"],
        summary="List tenant memberships.",
        responses={200: TenantMembershipSerializer(many=True), 403: ApiErrorResponseSerializer},
    ),
    create=extend_schema(
        operation_id="common_v1_tenant_memberships_create",
        tags=["Common - Tenant Membership Operations"],
        summary="Create or upsert tenant membership.",
        request=TenantMembershipSerializer,
        responses={201: TenantMembershipSerializer, 403: ApiErrorResponseSerializer},
    ),
    retrieve=extend_schema(
        operation_id="common_v1_tenant_memberships_retrieve",
        tags=["Common - Tenant Membership Operations"],
        summary="Retrieve tenant membership.",
        responses={
            200: TenantMembershipSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    ),
    update=extend_schema(
        operation_id="common_v1_tenant_memberships_update",
        tags=["Common - Tenant Membership Operations"],
        summary="Update tenant membership role/state.",
        request=TenantMembershipSerializer,
        responses={
            200: TenantMembershipSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    ),
    partial_update=extend_schema(
        operation_id="common_v1_tenant_memberships_partial_update",
        tags=["Common - Tenant Membership Operations"],
        summary="Partially update tenant membership role/state.",
        request=TenantMembershipSerializer,
        responses={
            200: TenantMembershipSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    ),
    destroy=extend_schema(
        operation_id="common_v1_tenant_memberships_destroy",
        tags=["Common - Tenant Membership Operations"],
        summary="Deactivate tenant membership.",
        responses={204: None, 403: ApiErrorResponseSerializer, 404: ApiErrorResponseSerializer},
    ),
    deactivate=extend_schema(
        operation_id="common_v1_tenant_memberships_deactivate",
        tags=["Common - Tenant Membership Operations"],
        summary="Deactivate tenant membership.",
        responses={
            200: TenantMembershipSerializer,
            403: ApiErrorResponseSerializer,
            404: ApiErrorResponseSerializer,
        },
    ),
)
