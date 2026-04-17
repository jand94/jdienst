from rest_framework import serializers


class AuthLoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(
        help_text="Username or email address.",
    )
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_username(self, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError("Username must not be empty.")
        return normalized


class AuthTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    token_type = serializers.CharField(default="Bearer")


class AuthNoopSerializer(serializers.Serializer):
    pass


class AuthLogoutResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()


class AuthErrorPayloadSerializer(serializers.Serializer):
    code = serializers.CharField()
    message = serializers.CharField()
    details = serializers.DictField(required=False)
    request_id = serializers.CharField(allow_null=True, required=False)
    trace_id = serializers.CharField(allow_null=True, required=False)


class AuthErrorEnvelopeSerializer(serializers.Serializer):
    error = AuthErrorPayloadSerializer()
