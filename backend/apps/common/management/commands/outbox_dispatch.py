from django.core.management.base import BaseCommand

from apps.common.api.v1.services import dispatch_pending_outbox_events


class Command(BaseCommand):
    help = "Dispatches pending outbox events."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100)

    def handle(self, *args, **options):
        result = dispatch_pending_outbox_events(batch_size=options["batch_size"])
        self.stdout.write(
            self.style.SUCCESS(
                "Outbox dispatch processed={processed} sent={sent} failed={failed}".format(**result)
            )
        )
