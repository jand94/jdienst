from django.contrib import admin

from apps.common.admin.audit_mixin import AdminAuditTrailMixin

class AuditBaseAdmin(AdminAuditTrailMixin, admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
