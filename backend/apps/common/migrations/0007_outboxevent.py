import uuid

from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0006_idempotencykey"),
    ]

    operations = [
        migrations.CreateModel(
            name="OutboxEvent",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("topic", models.CharField(db_index=True, max_length=128)),
                ("dedup_key", models.CharField(blank=True, db_index=True, default="", max_length=255)),
                ("payload", models.JSONField(default=dict)),
                ("headers", models.JSONField(blank=True, default=dict)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed")],
                        db_index=True,
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("attempts", models.PositiveIntegerField(default=0)),
                ("next_attempt_at", models.DateTimeField(db_index=True, default=timezone.now)),
                ("sent_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("last_error", models.TextField(blank=True, default="")),
            ],
            options={
                "indexes": [
                    models.Index(fields=["status", "next_attempt_at"], name="common_outb_status_3cd8ae_idx"),
                    models.Index(fields=["topic", "status"], name="common_outb_topic_b2f2b1_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(
                        condition=~models.Q(dedup_key=""),
                        fields=("topic", "dedup_key"),
                        name="common_outbox_topic_dedup_unique",
                    )
                ],
            },
        ),
    ]
