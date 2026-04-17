import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import backfill_integrity_hashes


class Command(BaseCommand):
    help = "Repariert Legacy-Audit-Events ohne/mit falschen Integritaetshashes."

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=0)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--source", type=str, default="management-command")

    def handle(self, *args, **options):
        result = backfill_integrity_hashes(
            dry_run=options["dry_run"],
            limit=options["limit"] or None,
            source=options["source"],
        )
        self.stdout.write(json.dumps(result, sort_keys=True))
