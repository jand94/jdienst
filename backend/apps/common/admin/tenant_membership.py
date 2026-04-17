from django.contrib import admin

from apps.common.admin.base_admin import AuditBaseAdmin
from apps.common.models import TenantMembership


@admin.register(TenantMembership)
class TenantMembershipAdmin(AuditBaseAdmin):
    list_display = ("tenant", "user", "role", "is_active", "created_at")
    list_filter = ("role", "is_active", "created_at")
    search_fields = ("tenant__slug", "tenant__name", "user__username", "user__email")
    actions = ("activate_memberships", "deactivate_memberships")

    @admin.action(description="Activate selected memberships")
    def activate_memberships(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Deactivate selected memberships")
    def deactivate_memberships(self, request, queryset):
        queryset.update(is_active=False)
