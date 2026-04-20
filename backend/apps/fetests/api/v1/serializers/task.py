from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.fetests.models import Task

User = get_user_model()


class TaskReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = (
            "id",
            "tenant",
            "title",
            "description",
            "status",
            "assignee",
            "assigned_by",
            "due_at",
            "completed_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        )
        read_only_fields = fields


class TaskCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    assignee_id = serializers.IntegerField(required=False)
    due_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_assignee_id(self, value: int) -> int:
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Assignee does not exist.")
        return value


class TaskUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(required=False, max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    due_at = serializers.DateTimeField(required=False, allow_null=True)


class TaskAssignSerializer(serializers.Serializer):
    assignee_id = serializers.IntegerField()

    def validate_assignee_id(self, value: int) -> int:
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Assignee does not exist.")
        return value
