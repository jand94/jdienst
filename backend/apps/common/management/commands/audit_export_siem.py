import json

from django.core.management.base import BaseCommand, CommandError

from apps.common.api.v1.services import export_events_for_siem, mark_events_exported


class Command(BaseCommand):
    help = "Exportiert Audit-Events als JSON Lines fuer SIEM."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=500)
        parser.add_argument("--mark-exported", action="store_true")
        parser.add_argument(
            "--fail-on-errors",
            action="store_true",
            help="Command mit Fehler beenden, wenn Export-Fehler auftreten.",
        )

    def handle(self, *args, **options):
        payloads, failures, exported_ids = export_events_for_siem(limit=options["limit"])
        for payload in payloads:
            self.stdout.write(json.dumps(payload, sort_keys=True))

        if failures:
            for failed in failures:
                self.stderr.write(
                    self.style.WARNING(
                        f"Failed event {failed['event_id']}: {failed['error']}",
                    )
                )
            if options["fail_on_errors"]:
                raise CommandError(f"SIEM export had {len(failures)} failures.")

        if options["mark_exported"]:
            marked = mark_events_exported(event_ids=exported_ids)
            self.stdout.write(self.style.SUCCESS(f"Marked exported events: {marked}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"SIEM export summary: exported={len(payloads)} failed={len(failures)}",
            )
        )
