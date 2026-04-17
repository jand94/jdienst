import json

from django.core.management.base import BaseCommand, CommandError

from apps.common.api.v1.services import collect_tenant_consistency_snapshot


class Command(BaseCommand):
    help = "Checks tenant consistency invariants."

    def add_arguments(self, parser):
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        payload = collect_tenant_consistency_snapshot()
        self.stdout.write(json.dumps(payload, sort_keys=True))
        if options["fail_on_error"] and not payload["passed"]:
            raise CommandError("Tenant consistency check failed.")
