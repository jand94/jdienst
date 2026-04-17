from django.core.management.base import BaseCommand

from apps.common.api.v1.services import archive_events_by_retention_policy, archive_old_events


class Command(BaseCommand):
    help = "Markiert alte Audit-Events als archiviert."

    def add_arguments(self, parser):
        parser.add_argument("--before-days", type=int, default=90)
        parser.add_argument(
            "--use-retention-policy",
            action="store_true",
            help="Archivierung anhand der Retention-Klassen statt fixer Tage.",
        )

    def handle(self, *args, **options):
        if options["use_retention_policy"]:
            affected = archive_events_by_retention_policy()
        else:
            affected = archive_old_events(before_days=options["before_days"])
        self.stdout.write(self.style.SUCCESS(f"Archived events: {affected}"))
