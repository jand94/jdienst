from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0003_auditintegritycheckpoint_auditintegrityverification"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditChainState",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True, db_index=True)),
                (
                    "id",
                    models.PositiveSmallIntegerField(
                        default=1,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("last_hash", models.CharField(blank=True, default="", max_length=64)),
            ],
            options={
                "verbose_name": "Audit chain state",
                "verbose_name_plural": "Audit chain state",
            },
        ),
    ]
