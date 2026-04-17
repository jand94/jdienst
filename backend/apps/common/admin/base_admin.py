from django.contrib import admin


class AuditBaseAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
