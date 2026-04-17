import json

from django.contrib import admin
from django.utils.html import format_html

from apps.common.admin.base_admin import AuditBaseAdmin
from apps.common.models import AuditIntegrityCheckpoint, AuditIntegrityVerification


@admin.register(AuditIntegrityCheckpoint)
class AuditIntegrityCheckpointAdmin(AuditBaseAdmin):
    list_display = ("sequence", "anchor_hash", "signer", "verified_at", "created_at")
    list_filter = ("signer", "verified_at", "created_at")
    search_fields = ("anchor_hash",)
    readonly_fields = AuditBaseAdmin.readonly_fields + (
        "sequence",
        "anchor_event",
        "anchor_hash",
        "signature",
        "signer",
        "verified_at",
        "pretty_metadata",
    )

    @admin.display(description="Metadata")
    def pretty_metadata(self, obj: AuditIntegrityCheckpoint):
        formatted = json.dumps(obj.metadata, indent=2, ensure_ascii=False, sort_keys=True)
        return format_html("<pre>{}</pre>", formatted)


@admin.register(AuditIntegrityVerification)
class AuditIntegrityVerificationAdmin(AuditBaseAdmin):
    list_display = ("created_at", "status", "checked_events", "finished_at")
    list_filter = ("status", "created_at")
    search_fields = ("status", "last_event_hash")
    readonly_fields = AuditBaseAdmin.readonly_fields + (
        "status",
        "checked_events",
        "last_event_hash",
        "checkpoint",
        "finished_at",
        "pretty_details",
    )

    @admin.display(description="Details")
    def pretty_details(self, obj: AuditIntegrityVerification):
        formatted = json.dumps(obj.details, indent=2, ensure_ascii=False, sort_keys=True)
        return format_html("<pre>{}</pre>", formatted)
