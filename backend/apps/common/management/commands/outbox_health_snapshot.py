import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import collect_outbox_health_snapshot


class Command(BaseCommand):
    help = "Prints outbox health indicators for operational checks."

    def handle(self, *args, **options):
        payload = collect_outbox_health_snapshot()
        self.stdout.write(json.dumps(payload, sort_keys=True))
