from rest_framework import serializers

from apps.accounts.models import User
from apps.common.models import TenantMembership


class AccountUserReadSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()
    feature_flags = serializers.SerializerMethodField()
    current_tenant_role = serializers.SerializerMethodField()
    navigation_favorites = serializers.ListField(child=serializers.CharField(), read_only=True)

    def _context_access(self) -> dict | None:
        access = self.context.get("access_context")
        if isinstance(access, dict):
            return access
        return None

    def get_permissions(self, instance) -> list[str]:
        access = self._context_access()
        if access is None:
            return []
        permissions = access.get("permissions")
        if isinstance(permissions, list):
            return [str(item) for item in permissions]
        return []

    def get_feature_flags(self, instance) -> list[str]:
        access = self._context_access()
        if access is None:
            return []
        feature_flags = access.get("feature_flags")
        if isinstance(feature_flags, list):
            return [str(item) for item in feature_flags]
        return []

    def get_current_tenant_role(self, instance) -> str | None:
        access = self._context_access()
        if access is None:
            return None
        role = access.get("current_tenant_role")
        if isinstance(role, str):
            return role
        return None

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
            "permissions",
            "feature_flags",
            "current_tenant_role",
            "navigation_favorites",
        )
        read_only_fields = fields


class AccountUserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)

    def validate_email(self, value: str) -> str:
        request = self.context.get("request")
        actor = getattr(request, "user", None)
        if actor is None:
            return value
        if User.objects.filter(email=value).exclude(pk=actor.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value


class AccountUserTenantMembershipSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source="tenant.id", read_only=True)
    tenant_slug = serializers.CharField(source="tenant.slug", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = TenantMembership
        fields = (
            "tenant_id",
            "tenant_slug",
            "tenant_name",
            "role",
            "is_active",
        )
        read_only_fields = fields


class AccountNavigationFavoritesSerializer(serializers.Serializer):
    favorites = serializers.ListField(child=serializers.CharField(max_length=128), allow_empty=True)

    def validate_favorites(self, value: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for favorite in value:
            item = favorite.strip()
            if not item.startswith("/"):
                raise serializers.ValidationError("Jeder Favorit muss mit '/' beginnen.")
            if item in seen:
                continue
            seen.add(item)
            normalized.append(item)
        return normalized
