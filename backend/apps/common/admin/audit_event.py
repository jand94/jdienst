import json

from django.contrib import admin
from django.utils.html import format_html

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
        "pretty_metadata",
        "ip_address",
        "user_agent",
    )

    @admin.display(description="Was geändert wurde")
    def pretty_metadata(self, obj: AuditEvent):
        formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False, sort_keys=True)
        return format_html("<pre>{}</pre>", formatted)
