from rest_framework import serializers

from apps.common.models import AuditEvent


class AuditReadOnlyFieldsSerializerMixin:
    audit_read_only_fields = ("created_at", "updated_at", "created_by", "updated_by")

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        for field_name in self.audit_read_only_fields:
            field_kwargs = extra_kwargs.get(field_name, {})
            field_kwargs["read_only"] = True
            extra_kwargs[field_name] = field_kwargs
        return extra_kwargs


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = (
            "id",
            "actor",
            "action",
            "target_model",
            "target_id",
            "metadata",
            "ip_address",
            "user_agent",
            "previous_hash",
            "integrity_hash",
            "archived_at",
            "exported_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "actor",
            "action",
            "target_model",
            "target_id",
            "metadata",
            "ip_address",
            "user_agent",
            "previous_hash",
            "integrity_hash",
            "archived_at",
            "exported_at",
            "created_at",
            "updated_at",
        )
