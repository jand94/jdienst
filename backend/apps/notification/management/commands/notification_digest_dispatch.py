from django.core.management.base import BaseCommand

from apps.notification.api.v1.services import dispatch_pending_digests


class Command(BaseCommand):
    help = "Dispatch pending notification digests immediately."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=50,
            help="Maximum number of pending digests to dispatch.",
        )

    def handle(self, *args, **options):
        processed = dispatch_pending_digests(limit=max(1, int(options["limit"])))
        self.stdout.write(f"digests_processed={processed}")
