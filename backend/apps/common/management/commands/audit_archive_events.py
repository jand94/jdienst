from django.core.management.base import BaseCommand

from apps.common.api.v1.services import archive_old_events


class Command(BaseCommand):
    help = "Markiert alte Audit-Events als archiviert."

    def add_arguments(self, parser):
        parser.add_argument("--before-days", type=int, default=90)

    def handle(self, *args, **options):
        affected = archive_old_events(before_days=options["before_days"])
        self.stdout.write(self.style.SUCCESS(f"Archived events: {affected}"))
