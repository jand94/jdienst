from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from apps.common.api.v1.services import record_audit_event
from apps.common.models import AuditEvent


class AdminAuditTrailMixin:
    audit_event_source = "django-admin"

    def _normalize_metadata_value(self, value):
        if isinstance(value, (datetime, date, time)):
            return value.isoformat()
        if isinstance(value, (UUID, Decimal)):
            return str(value)
        return value

    def _build_change_set(self, *, obj, changed_fields=None):
        if not obj.pk:
            return {}

        old_obj = obj.__class__.objects.filter(pk=obj.pk).first()
        if old_obj is None:
            return {}

        if changed_fields:
            candidate_fields = [field for field in obj._meta.concrete_fields if field.name in changed_fields]
        else:
            candidate_fields = obj._meta.concrete_fields

        changes = {}
        for field in candidate_fields:
            old_value = getattr(old_obj, field.attname)
            new_value = getattr(obj, field.attname)
            if old_value == new_value:
                continue
            changes[field.name] = {
                "old": self._normalize_metadata_value(old_value),
                "new": self._normalize_metadata_value(new_value),
            }
        return changes

    def _record_admin_event(self, *, request, action: str, obj) -> None:
        if isinstance(obj, AuditEvent):
            return

        metadata = {
            "source": self.audit_event_source,
            "model_name": obj._meta.model_name,
        }
        if action == "admin.update":
            changed_fields = getattr(request, "_admin_change_set", None)
            if changed_fields is None:
                changed_fields = self._build_change_set(
                    obj=obj,
                    changed_fields=getattr(request, "_admin_changed_fields", None),
                )
            if changed_fields:
                metadata["changes"] = changed_fields

        record_audit_event(
            action=action,
            target_model=obj._meta.label,
            target_id=str(obj.pk),
            actor=getattr(request, "user", None),
            metadata=metadata,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

    def save_model(self, request, obj, form, change):
        request._admin_changed_fields = (
            tuple(getattr(form, "changed_data", ())) if form is not None else None
        )
        request._admin_change_set = (
            self._build_change_set(
                obj=obj,
                changed_fields=request._admin_changed_fields,
            )
            if change
            else None
        )
        if hasattr(obj, "updated_by"):
            obj.updated_by = request.user
        if not change and hasattr(obj, "created_by"):
            obj.created_by = request.user

        super().save_model(request, obj, form, change)
        self._record_admin_event(
            request=request,
            action="admin.update" if change else "admin.create",
            obj=obj,
        )

    def delete_model(self, request, obj):
        target_id = str(obj.pk)
        target_model = obj._meta.label
        actor = getattr(request, "user", None)
        ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        super().delete_model(request, obj)

        if isinstance(obj, AuditEvent):
            return

        record_audit_event(
            action="admin.delete",
            target_model=target_model,
            target_id=target_id,
            actor=actor,
            metadata={
                "source": self.audit_event_source,
                "model_name": obj._meta.model_name,
            },
            ip_address=ip_address,
            user_agent=user_agent,
        )
