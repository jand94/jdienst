import json

from django.core.management.base import BaseCommand, CommandError

from apps.common.api.v1.services import lock_scope, run_platform_check


class Command(BaseCommand):
    help = "Runs enterprise platform checks for audit/idempotency/outbox health."

    def add_arguments(self, parser):
        parser.add_argument("--window-hours", type=int, default=24)
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        with lock_scope(key="common.platform_check", owner="management:common_platform_check", ttl_seconds=60):
            payload = run_platform_check(window_hours=options["window_hours"])
        self.stdout.write(json.dumps(payload, sort_keys=True))
        if options["fail_on_error"] and not payload["passed"]:
            raise CommandError("Platform check failed.")
