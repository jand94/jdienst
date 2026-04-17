import json

from django.core.management.base import BaseCommand, CommandError

from apps.common.api.v1.services import collect_audit_health_snapshot


class Command(BaseCommand):
    help = "Erzeugt einen Health-Snapshot fuer Audit-Monitoring und Alerting."

    def add_arguments(self, parser):
        parser.add_argument("--window-hours", type=int, default=24)
        parser.add_argument(
            "--require-fresh-integrity",
            action="store_true",
            help="Bricht mit Fehler ab, wenn kein frischer Integritaetsnachweis vorliegt.",
        )
        parser.add_argument(
            "--max-unexported-events",
            type=int,
            default=-1,
            help="Bricht mit Fehler ab, wenn mehr nicht exportierte Events vorhanden sind.",
        )

    def handle(self, *args, **options):
        snapshot = collect_audit_health_snapshot(window_hours=options["window_hours"])
        if options["require_fresh_integrity"] and not snapshot["integrity_verification"]["is_fresh"]:
            raise CommandError("Integrity verification is stale or missing.")
        max_unexported = options["max_unexported_events"]
        if max_unexported >= 0 and snapshot["events_not_exported"] > max_unexported:
            raise CommandError(
                "Too many unexported events: "
                f"{snapshot['events_not_exported']} > {max_unexported}",
            )
        self.stdout.write(json.dumps(snapshot, sort_keys=True))
