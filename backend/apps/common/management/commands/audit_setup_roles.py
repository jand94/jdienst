from django.core.management.base import BaseCommand

from apps.common.api.v1.services import ensure_audit_reader_roles


class Command(BaseCommand):
    help = "Erzeugt/aktualisiert Audit-Reader-Rollen mit den benoetigten Permissions."

    def handle(self, *args, **options):
        role_names, created_total = ensure_audit_reader_roles()
        for role_name in role_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Role '{role_name}' ready with permission common.view_auditevent",
                )
            )
        self.stdout.write(self.style.SUCCESS(f"Created roles: {created_total}"))
