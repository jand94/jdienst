import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0005_auditevent_operator_permission"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="IdempotencyKey",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("scope", models.CharField(db_index=True, max_length=128)),
                ("key", models.CharField(max_length=255)),
                ("actor_identifier", models.CharField(db_index=True, max_length=64)),
                ("request_fingerprint", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[("in_progress", "In progress"), ("completed", "Completed"), ("failed", "Failed")],
                        db_index=True,
                        default="in_progress",
                        max_length=16,
                    ),
                ),
                ("response_code", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("response_payload", models.JSONField(blank=True, default=dict)),
                ("error_payload", models.JSONField(blank=True, default=dict)),
                ("last_seen_at", models.DateTimeField(auto_now=True)),
                ("expires_at", models.DateTimeField(db_index=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="idempotency_keys",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["scope", "status", "expires_at"], name="common_idem_scope_33458a_idx"),
                    models.Index(fields=["expires_at"], name="common_idem_expires_18f86f_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("scope", "key", "actor_identifier"),
                        name="common_idempotency_scope_key_actor_unique",
                    )
                ],
            },
        ),
    ]
