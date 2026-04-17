from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.common.models import Tenant, TenantMembership


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = (
            "id",
            "slug",
            "name",
            "status",
            "settings",
            "deleted_at",
            "delete_reason",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "deleted_at", "created_at", "updated_at")


class TenantStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Tenant.STATUS_CHOICES)


class TenantMembershipSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(source="user", queryset=get_user_model().objects.all())
    tenant_id = serializers.PrimaryKeyRelatedField(source="tenant", queryset=Tenant.all_objects.all())

    class Meta:
        model = TenantMembership
        fields = (
            "id",
            "tenant_id",
            "user_id",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
