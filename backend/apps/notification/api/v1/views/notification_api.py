from __future__ import annotations

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.viewsets import GenericViewSet

from apps.common.api.v1.services import ensure_user_in_tenant, extract_audit_correlation_ids, require_tenant
from apps.common.api.v1.serializers import PlatformHealthQuerySerializer
from apps.common.models import TenantMembership
from apps.notification.api.v1.permissions import IsNotificationOperator, IsStaffNotificationWriter
from apps.notification.api.v1.schema import (
    notification_bulk_mark_read_schema,
    notification_mark_read_schema,
    notification_ops_snapshot_schema,
    notification_preference_viewset_schema,
    notification_viewset_schema,
)
from apps.notification.api.v1.serializers import (
    NotificationBulkMarkReadSerializer,
    NotificationCreateSerializer,
    NotificationPreferenceReadSerializer,
    NotificationPreferenceUpdateSerializer,
    NotificationReadSerializer,
)
from apps.notification.api.v1.services import (
    create_notification,
    list_notifications_for_user,
    list_user_preferences,
    mark_notification_as_read,
    mark_notifications_as_read_bulk,
    set_user_preference,
    collect_notification_health_snapshot,
)
from apps.notification.models import Notification, NotificationType

User = get_user_model()


@notification_viewset_schema
class NotificationViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NotificationReadSerializer
    throttle_classes = [ScopedRateThrottle]

    def get_permissions(self):
        if self.action == "create":
            return [IsAuthenticated(), IsStaffNotificationWriter()]
        return [IsAuthenticated()]

    def get_throttles(self):
        if self.action == "create":
            self.throttle_scope = "notification_create"
        elif self.action == "mark_read":
            self.throttle_scope = "notification_mark_read"
        elif self.action == "bulk_mark_read":
            self.throttle_scope = "notification_bulk_mark_read"
        else:
            self.throttle_scope = None
        return super().get_throttles()

    def get_queryset(self):
        tenant = require_tenant(self.request)
        ensure_user_in_tenant(user=self.request.user, tenant=tenant)
        include_archived = self.request.query_params.get("include_archived", "").lower() in {"1", "true", "yes"}
        return list_notifications_for_user(
            tenant=tenant,
            user=self.request.user,
            include_archived=include_archived,
        )

    def create(self, request, *args, **kwargs):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        recipient = get_object_or_404(User, pk=payload["recipient_id"])
        is_member = TenantMembership.objects.filter(
            tenant=tenant,
            user=recipient,
            is_active=True,
        ).exists()
        if not is_member:
            raise ValidationError({"recipient_id": "Recipient is not an active member of the tenant."})
        request_id, trace_id = extract_audit_correlation_ids(request)
        notification = create_notification(
            tenant=tenant,
            actor=request.user,
            recipient=recipient,
            notification_type_key=payload["notification_type_key"],
            title=payload["title"],
            body=payload["body"],
            metadata=payload.get("metadata", {}),
            dedup_key=payload.get("dedup_key", ""),
            channels=payload.get("channels"),
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(NotificationReadSerializer(notification).data, status=status.HTTP_201_CREATED)

    @notification_mark_read_schema
    @action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        notification = get_object_or_404(Notification.objects.select_related("notification_type"), pk=pk)
        request_id, trace_id = extract_audit_correlation_ids(request)
        updated = mark_notification_as_read(
            tenant=tenant,
            actor=request.user,
            notification=notification,
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(NotificationReadSerializer(updated).data)

    @notification_bulk_mark_read_schema
    @action(detail=False, methods=["post"], url_path="bulk-mark-read")
    def bulk_mark_read(self, request):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        serializer = NotificationBulkMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_id, trace_id = extract_audit_correlation_ids(request)
        count = mark_notifications_as_read_bulk(
            tenant=tenant,
            actor=request.user,
            notification_ids=[str(item) for item in serializer.validated_data["notification_ids"]],
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response({"updated": count}, status=status.HTTP_200_OK)


@notification_preference_viewset_schema
class NotificationPreferenceViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = NotificationPreferenceReadSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]

    def get_throttles(self):
        self.throttle_scope = "notification_preference_update" if self.action in {"create"} else None
        return super().get_throttles()

    def get_queryset(self):
        tenant = require_tenant(self.request)
        ensure_user_in_tenant(user=self.request.user, tenant=tenant)
        return list_user_preferences(user=self.request.user)

    def create(self, request, *args, **kwargs):
        tenant = require_tenant(request)
        ensure_user_in_tenant(user=request.user, tenant=tenant)
        serializer = NotificationPreferenceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        notification_type = get_object_or_404(
            NotificationType,
            key=serializer.validated_data["notification_type_key"],
            is_active=True,
        )
        request_id, trace_id = extract_audit_correlation_ids(request)
        preference = set_user_preference(
            user=request.user,
            notification_type=notification_type,
            channel=serializer.validated_data["channel"],
            is_subscribed=serializer.validated_data["is_subscribed"],
            request_id=request_id,
            trace_id=trace_id,
        )
        return Response(
            NotificationPreferenceReadSerializer(preference).data,
            status=status.HTTP_201_CREATED,
        )


class NotificationOpsViewSet(GenericViewSet):
    permission_classes = [IsNotificationOperator]
    serializer_class = PlatformHealthQuerySerializer
    throttle_classes = [ScopedRateThrottle]

    def get_throttles(self):
        self.throttle_scope = "notification_ops_snapshot" if self.action == "health_snapshot" else None
        return super().get_throttles()

    @notification_ops_snapshot_schema
    @action(detail=False, methods=["get"], url_path="health-snapshot")
    def health_snapshot(self, request):
        serializer = self.serializer_class(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        payload = collect_notification_health_snapshot(
            window_hours=serializer.validated_data.get("window_hours", 24),
        )
        return Response(payload, status=status.HTTP_200_OK)
