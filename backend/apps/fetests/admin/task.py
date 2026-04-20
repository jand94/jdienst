from django.contrib import admin

from apps.common.admin import AuditBaseAdmin
from apps.fetests.models import Task


@admin.register(Task)
class TaskAdmin(AuditBaseAdmin):
    list_display = ("id", "title", "tenant", "status", "assignee", "assigned_by", "due_at", "completed_at")
    list_filter = ("status", "tenant")
    search_fields = ("title", "description")
    readonly_fields = AuditBaseAdmin.readonly_fields + ("completed_at",)
