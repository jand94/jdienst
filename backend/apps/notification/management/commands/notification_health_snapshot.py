import json

from django.core.management.base import BaseCommand

from apps.notification.api.v1.services import collect_notification_health_snapshot


class Command(BaseCommand):
    help = "Print notification pipeline health and SLO indicators."

    def add_arguments(self, parser):
        parser.add_argument(
            "--window-hours",
            type=int,
            default=24,
            help="Observation window in hours for success/failure rates.",
        )

    def handle(self, *args, **options):
        payload = collect_notification_health_snapshot(window_hours=max(1, int(options["window_hours"])))
        self.stdout.write(json.dumps(payload, sort_keys=True))
