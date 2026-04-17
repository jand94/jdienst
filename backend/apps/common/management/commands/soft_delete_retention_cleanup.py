import json

from django.core.management.base import BaseCommand

from apps.common.api.v1.services import cleanup_soft_deleted_tenants


class Command(BaseCommand):
    help = "Hard-deletes soft-deleted technical records after retention period."

    def add_arguments(self, parser):
        parser.add_argument("--older-than-days", type=int, default=30)

    def handle(self, *args, **options):
        deleted_count = cleanup_soft_deleted_tenants(older_than_days=options["older_than_days"])
        payload = {
            "model": "common.Tenant",
            "hard_deleted": deleted_count,
            "older_than_days": options["older_than_days"],
        }
        self.stdout.write(json.dumps(payload, sort_keys=True))
