from django.core.management.base import BaseCommand

from apps.notification.api.v1.services import build_pending_digests


class Command(BaseCommand):
    help = "Build pending notification digests for unread notifications."

    def handle(self, *args, **options):
        created = build_pending_digests()
        self.stdout.write(f"digests_created={created}")
