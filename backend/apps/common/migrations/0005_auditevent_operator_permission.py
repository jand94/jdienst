from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0004_auditchainstate"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="auditevent",
            options={
                "ordering": ("-created_at",),
                "permissions": [
                    ("operate_auditevent", "Can execute audit operator actions"),
                ],
            },
        ),
    ]
