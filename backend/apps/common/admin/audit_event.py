from django.contrib import admin

from apps.common.admin.base_admin import AuditBaseAdmin
from apps.common.models import AuditEvent


@admin.register(AuditEvent)
class AuditEventAdmin(AuditBaseAdmin):
    list_display = ("created_at", "action", "target_model", "target_id", "actor")
    list_filter = ("action", "target_model", "created_at")
    search_fields = ("action", "target_model", "target_id", "actor__username", "actor__email")
    readonly_fields = AuditBaseAdmin.readonly_fields + (
        "action",
        "target_model",
        "target_id",
        "actor",
        "metadata",
        "ip_address",
        "user_agent",
    )
