import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0007_outboxevent"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DistributedLock",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=128, unique=True)),
                ("owner", models.CharField(max_length=128)),
                ("token", models.CharField(max_length=128)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["expires_at"], name="common_dlock_exp_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="Tenant",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("deleted_at", models.DateTimeField(blank=True, db_index=True, null=True)),
                ("delete_reason", models.CharField(blank=True, default="", max_length=255)),
                ("slug", models.SlugField(db_index=True, max_length=64, unique=True)),
                ("name", models.CharField(max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("active", "Active"), ("suspended", "Suspended"), ("archived", "Archived")],
                        db_index=True,
                        default="active",
                        max_length=16,
                    ),
                ),
                ("settings", models.JSONField(blank=True, default=dict)),
                (
                    "deleted_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="common_tenant_deleted",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["status", "slug"], name="common_tnt_stat_slug_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="TenantMembership",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "role",
                    models.CharField(
                        choices=[("owner", "Owner"), ("admin", "Admin"), ("member", "Member")],
                        db_index=True,
                        default="member",
                        max_length=16,
                    ),
                ),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "tenant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="memberships", to="common.tenant"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tenant_memberships",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(fields=["tenant", "is_active"], name="common_tmem_tnt_act_idx"),
                    models.Index(fields=["user", "is_active"], name="common_tmem_usr_act_idx"),
                ],
                "constraints": [
                    models.UniqueConstraint(fields=("tenant", "user"), name="common_tenant_membership_unique"),
                ],
            },
        ),
    ]
