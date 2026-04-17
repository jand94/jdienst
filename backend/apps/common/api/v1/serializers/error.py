from rest_framework import serializers


class ApiErrorPayloadSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.JSONField()
    request_id = serializers.CharField(allow_null=True, required=False)
    trace_id = serializers.CharField(allow_null=True, required=False)


class ApiErrorResponseSerializer(serializers.Serializer):
    error = ApiErrorPayloadSerializer()
