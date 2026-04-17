import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import build_siem_payload, mark_events_exported
from apps.common.models import AuditEvent


class Command(BaseCommand):
    help = "Exportiert Audit-Events als JSON Lines fuer SIEM."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=500)
        parser.add_argument("--mark-exported", action="store_true")

    def handle(self, *args, **options):
        qs = AuditEvent.objects.filter(exported_at__isnull=True).order_by("created_at")[: options["limit"]]
        exported_ids: list[str] = []
        for event in qs:
            self.stdout.write(json.dumps(build_siem_payload(event), sort_keys=True))
            exported_ids.append(str(event.pk))

        if options["mark_exported"]:
            marked = mark_events_exported(event_ids=exported_ids)
            self.stdout.write(self.style.SUCCESS(f"Marked exported events: {marked}"))
