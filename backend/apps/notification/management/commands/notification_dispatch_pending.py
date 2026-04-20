from django.core.management.base import BaseCommand

from apps.notification.api.v1.services import dispatch_pending_deliveries


class Command(BaseCommand):
    help = "Dispatch due pending notification deliveries immediately."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=200,
            help="Maximum number of pending deliveries to process.",
        )

    def handle(self, *args, **options):
        dispatched = dispatch_pending_deliveries(limit=max(1, int(options["limit"])))
        self.stdout.write(f"dispatched={dispatched}")
