from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.api.v1.permissions import IsAuditOperator
from apps.common.api.v1.schema import (
    tenant_membership_ops_viewset_schema,
    tenant_ops_viewset_schema,
)
from apps.common.api.v1.serializers import (
    TenantMembershipSerializer,
    TenantSerializer,
    TenantStatusUpdateSerializer,
)
from apps.common.api.v1.services import (
    deactivate_tenant_membership,
    extract_audit_correlation_ids,
    assign_user_to_tenant,
    record_audit_event,
)
from apps.common.models import Tenant, TenantMembership


@tenant_ops_viewset_schema
class TenantOperationsViewSet(ModelViewSet):
    permission_classes = [IsAuditOperator]
    serializer_class = TenantSerializer
    queryset = Tenant.all_objects.order_by("slug")

    def perform_create(self, serializer):
        tenant = serializer.save()
        request_id, trace_id = extract_audit_correlation_ids(self.request)
        record_audit_event(
            action="common.tenant.created",
            target_model="common.Tenant",
            target_id=str(tenant.pk),
            actor=self.request.user,
            metadata={"source": "api", "tenant_slug": tenant.slug},
            request_id=request_id,
            trace_id=trace_id,
        )

    def perform_update(self, serializer):
        tenant = serializer.save()
        request_id, trace_id = extract_audit_correlation_ids(self.request)
        record_audit_event(
            action="common.tenant.updated",
            target_model="common.Tenant",
            target_id=str(tenant.pk),
            actor=self.request.user,
            metadata={"source": "api", "tenant_slug": tenant.slug, "status": tenant.status},
            request_id=request_id,
            trace_id=trace_id,
        )

    def destroy(self, request, *args, **kwargs):
        tenant = self.get_object()
        tenant.soft_delete(actor=request.user, reason="ops_api")
        request_id, trace_id = extract_audit_correlation_ids(request)
        record_audit_event(
            action="common.tenant.deactivated",
            target_model="common.Tenant",
            target_id=str(tenant.pk),
            actor=request.user,
            metadata={"source": "api", "tenant_slug": tenant.slug},
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        tenant = self.get_object()
        serializer = TenantStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant.status = serializer.validated_data["status"]
        tenant.save(update_fields=("status", "updated_at"))
        request_id, trace_id = extract_audit_correlation_ids(request)
        record_audit_event(
            action="common.tenant.status_changed",
            target_model="common.Tenant",
            target_id=str(tenant.pk),
            actor=request.user,
            metadata={"source": "api", "tenant_slug": tenant.slug, "status": tenant.status},
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(self.get_serializer(tenant).data)


@tenant_membership_ops_viewset_schema
class TenantMembershipOperationsViewSet(ModelViewSet):
    permission_classes = [IsAuditOperator]
    serializer_class = TenantMembershipSerializer
    queryset = TenantMembership.objects.select_related("tenant", "user").order_by("tenant__slug", "user_id")

    def perform_create(self, serializer):
        request_id, trace_id = extract_audit_correlation_ids(self.request)
        validated = serializer.validated_data
        membership = assign_user_to_tenant(
            user=validated["user"],
            tenant=validated["tenant"],
            role=validated["role"],
            is_active=validated.get("is_active", True),
            actor=self.request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        serializer.instance = membership

    def perform_update(self, serializer):
        request_id, trace_id = extract_audit_correlation_ids(self.request)
        validated = serializer.validated_data
        membership = assign_user_to_tenant(
            user=validated.get("user", serializer.instance.user),
            tenant=validated.get("tenant", serializer.instance.tenant),
            role=validated.get("role", serializer.instance.role),
            is_active=validated.get("is_active", serializer.instance.is_active),
            actor=self.request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        serializer.instance = membership

    @action(detail=True, methods=["post"], url_path="deactivate")
    def deactivate(self, request, pk=None):
        request_id, trace_id = extract_audit_correlation_ids(request)
        membership = self.get_object()
        deactivate_tenant_membership(
            membership=membership,
            actor=request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(self.get_serializer(membership).data)

    def destroy(self, request, *args, **kwargs):
        request_id, trace_id = extract_audit_correlation_ids(request)
        membership = self.get_object()
        deactivate_tenant_membership(
            membership=membership,
            actor=request.user,
            source="api",
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
