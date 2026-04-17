from django.core.management.base import BaseCommand, CommandError

from apps.common.api.v1.services import verify_integrity_chain
from apps.common.exceptions import InvalidAuditEvent
from apps.common.models import AuditIntegrityVerification


class Command(BaseCommand):
    help = "Prueft die Integritaetskette der Audit-Events und erzeugt Verifikationsnachweise."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--create-checkpoint", action="store_true")
        parser.add_argument("--source", type=str, default="management-command")
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        try:
            verification = verify_integrity_chain(
                limit=options["limit"] or None,
                create_checkpoint=options["create_checkpoint"],
                source=options["source"],
            )
        except InvalidAuditEvent as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(
            self.style.SUCCESS(
                "Integrity verification status="
                f"{verification.status} checked_events={verification.checked_events}",
            )
        )
        if (
            options["fail_on_error"]
            and verification.status == AuditIntegrityVerification.STATUS_FAILED
        ):
            raise CommandError("Integrity verification failed.")
