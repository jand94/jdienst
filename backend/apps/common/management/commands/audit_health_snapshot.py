import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import collect_audit_health_snapshot


class Command(BaseCommand):
    help = "Erzeugt einen Health-Snapshot fuer Audit-Monitoring und Alerting."

    def add_arguments(self, parser):
        parser.add_argument("--window-hours", type=int, default=24)

    def handle(self, *args, **options):
        snapshot = collect_audit_health_snapshot(window_hours=options["window_hours"])
        self.stdout.write(json.dumps(snapshot, sort_keys=True))
