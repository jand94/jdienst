from rest_framework import serializers

from apps.accounts.models import User


class AccountUserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
        )
        read_only_fields = fields


class AccountUserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False)

    def validate_email(self, value: str) -> str:
        request = self.context.get("request")
        actor = getattr(request, "user", None)
        if actor is None:
            return value
        if User.objects.filter(email=value).exclude(pk=actor.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value
