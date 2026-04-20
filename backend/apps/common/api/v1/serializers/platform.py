from rest_framework import serializers


class PlatformHealthQuerySerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=720, default=24)


class PlatformOperationNoInputSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=720, default=24)


class PlatformSoftDeleteCleanupRequestSerializer(serializers.Serializer):
    older_than_days = serializers.IntegerField(required=False, min_value=1, max_value=3650, default=30)


class PlatformHealthResponseSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField()
    audit = serializers.JSONField()
    idempotency = serializers.JSONField()
    outbox = serializers.JSONField()
    tenant = serializers.JSONField()
    notification = serializers.JSONField(required=False, allow_null=True)


class PlatformCheckResponseSerializer(serializers.Serializer):
    passed = serializers.BooleanField()
    checks = serializers.ListField(child=serializers.JSONField())
    snapshot = serializers.JSONField()


class PlatformSloReportResponseSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField()
    check_passed = serializers.BooleanField()
    idempotency_cleaned_records = serializers.IntegerField()
    soft_deleted_tenants_cleaned = serializers.IntegerField()
    check_summary = serializers.ListField(child=serializers.JSONField())
