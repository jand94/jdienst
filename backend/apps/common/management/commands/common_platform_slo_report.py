import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import run_platform_slo_report


class Command(BaseCommand):
    help = "Generates a platform SLO report and maintenance summary."

    def add_arguments(self, parser):
        parser.add_argument("--window-hours", type=int, default=24)

    def handle(self, *args, **options):
        payload = run_platform_slo_report(window_hours=options["window_hours"])
        self.stdout.write(json.dumps(payload, sort_keys=True))
