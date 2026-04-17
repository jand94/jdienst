from django.core.management.base import BaseCommand

from apps.common.api.v1.services import ensure_audit_operator_roles, ensure_audit_reader_roles


class Command(BaseCommand):
    help = "Erzeugt/aktualisiert Audit-Reader- und Audit-Operator-Rollen mit benoetigten Permissions."

    def handle(self, *args, **options):
        reader_role_names, reader_created_total = ensure_audit_reader_roles()
        operator_role_names, operator_created_total = ensure_audit_operator_roles()

        for role_name in reader_role_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Role '{role_name}' ready with permission common.view_auditevent",
                )
            )
        for role_name in operator_role_names:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Role '{role_name}' ready with permission common.operate_auditevent",
                )
            )

        total_created = reader_created_total + operator_created_total
        self.stdout.write(self.style.SUCCESS(f"Created roles: {total_created}"))
