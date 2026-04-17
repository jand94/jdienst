from django.contrib import admin

from apps.common.admin.base_admin import AuditBaseAdmin
from apps.common.models import Tenant


@admin.register(Tenant)
class TenantAdmin(AuditBaseAdmin):
    list_display = ("slug", "name", "status", "deleted_at", "created_at")
    list_filter = ("status", "deleted_at", "created_at")
    search_fields = ("slug", "name")
    readonly_fields = AuditBaseAdmin.readonly_fields + ("deleted_at",)
    ordering = ("slug",)
