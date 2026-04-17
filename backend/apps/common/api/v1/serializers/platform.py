from rest_framework import serializers


class PlatformHealthQuerySerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=720, default=24)


class PlatformOperationNoInputSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField(required=False, min_value=1, max_value=720, default=24)


class PlatformHealthResponseSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField()
    audit = serializers.JSONField()
    idempotency = serializers.JSONField()
    outbox = serializers.JSONField()


class PlatformCheckResponseSerializer(serializers.Serializer):
    passed = serializers.BooleanField()
    checks = serializers.ListField(child=serializers.JSONField())
    snapshot = serializers.JSONField()


class PlatformSloReportResponseSerializer(serializers.Serializer):
    window_hours = serializers.IntegerField()
    check_passed = serializers.BooleanField()
    idempotency_cleaned_records = serializers.IntegerField()
    check_summary = serializers.ListField(child=serializers.JSONField())
