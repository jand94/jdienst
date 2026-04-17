from rest_framework import serializers

from apps.common.api.v1.services.audit_integrity_service import AUDIT_INTEGRITY_MAX_LIMIT
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


class AuditIntegrityVerifyRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=AUDIT_INTEGRITY_MAX_LIMIT)
    create_checkpoint = serializers.BooleanField(required=False, default=False)


class AuditArchiveRequestSerializer(serializers.Serializer):
    before_days = serializers.IntegerField(required=False, min_value=1, max_value=36500, default=90)
    use_retention_policy = serializers.BooleanField(required=False, default=False)


class AuditHealthSnapshotQuerySerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=720, default=24)


class AuditSiemExportPreviewQuerySerializer(serializers.Serializer):
    limit = serializers.IntegerField(required=False, min_value=1, max_value=500, default=100)


class AuditNoInputSerializer(serializers.Serializer):
    pass


class AuditHealthSnapshotResponseSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField()
    events_total = serializers.IntegerField()
    events_without_actor = serializers.IntegerField()
    events_not_exported = serializers.IntegerField()
    retention_class_counts = serializers.DictField(child=serializers.IntegerField())
    volume_by_action = serializers.DictField(child=serializers.IntegerField())
    integrity_verification = serializers.JSONField()


class AuditIntegrityVerifyResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    status = serializers.CharField()
    checked_events = serializers.IntegerField()
    last_event_hash = serializers.CharField()
    details = serializers.JSONField()
    checkpoint_id = serializers.UUIDField(allow_null=True)


class AuditSiemExportPreviewResponseSerializer(serializers.Serializer):
    exportable_count = serializers.IntegerField()
    failure_count = serializers.IntegerField()
    event_ids = serializers.ListField(child=serializers.CharField())
    preview = serializers.ListField(child=serializers.JSONField())
    failures = serializers.ListField(child=serializers.JSONField())


class AuditArchiveResponseSerializer(serializers.Serializer):
    archived_events = serializers.IntegerField()
    mode = serializers.ChoiceField(choices=["before_days", "retention_policy"])


class AuditSetupRolesResponseSerializer(serializers.Serializer):
    roles = serializers.ListField(child=serializers.CharField())
    created_roles = serializers.IntegerField()
