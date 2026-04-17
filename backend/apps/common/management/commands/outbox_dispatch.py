from django.core.management.base import BaseCommand

from apps.common.api.v1.services import dispatch_pending_outbox_events, lock_scope


class Command(BaseCommand):
    help = "Dispatches pending outbox events."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100)

    def handle(self, *args, **options):
        with lock_scope(key="common.outbox_dispatch", owner="management:outbox_dispatch", ttl_seconds=60):
            result = dispatch_pending_outbox_events(batch_size=options["batch_size"])
        self.stdout.write(
            self.style.SUCCESS(
                "Outbox dispatch processed={processed} sent={sent} failed={failed}".format(**result)
            )
        )
