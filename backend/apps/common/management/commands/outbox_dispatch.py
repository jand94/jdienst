from django.core.management.base import BaseCommand

from apps.common.api.v1.services import dispatch_pending_outbox_events, lock_scope, requeue_failed_outbox_events


class Command(BaseCommand):
    help = "Dispatches pending outbox events."

    def add_arguments(self, parser):
        parser.add_argument("--batch-size", type=int, default=100)
        parser.add_argument("--replay-failed-limit", type=int, default=0)
        parser.add_argument("--replay-topic", type=str, default="")

    def handle(self, *args, **options):
        replayed = {"selected": 0, "requeued": 0}
        with lock_scope(key="common.outbox_dispatch", owner="management:outbox_dispatch", ttl_seconds=60):
            replay_limit = int(options.get("replay_failed_limit", 0))
            if replay_limit > 0:
                replayed = requeue_failed_outbox_events(
                    limit=replay_limit,
                    topic=options.get("replay_topic", ""),
                )
            result = dispatch_pending_outbox_events(batch_size=options["batch_size"])
        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Outbox dispatch replay_selected={replay_selected} replayed={replayed} "
                    "processed={processed} sent={sent} failed={failed}"
                ).format(
                    replay_selected=replayed["selected"],
                    replayed=replayed["requeued"],
                    **result,
                )
            )
        )
