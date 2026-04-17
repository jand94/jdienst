from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Erzeugt/aktualisiert Audit-Reader-Rollen mit den benoetigten Permissions."

    def handle(self, *args, **options):
        role_names = getattr(settings, "AUDIT_READER_GROUPS", ["AuditReader"])
        permission = Permission.objects.get(codename="view_auditevent")
        created_total = 0
        for role_name in role_names:
            group, created = Group.objects.get_or_create(name=role_name)
            group.permissions.add(permission)
            created_total += int(created)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Role '{role_name}' ready with permission common.view_auditevent",
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Created roles: {created_total}"))
