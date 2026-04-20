from __future__ import annotations

from celery import shared_task

from apps.notification.api.v1.services import (
    build_pending_digests,
    dispatch_pending_deliveries,
    dispatch_pending_digests,
)


@shared_task(name="notification.dispatch_pending_deliveries")
def run_notification_delivery_dispatch() -> int:
    return dispatch_pending_deliveries()


@shared_task(name="notification.build_pending_digests")
def run_notification_digest_build() -> int:
    return build_pending_digests()


@shared_task(name="notification.dispatch_pending_digests")
def run_notification_digest_dispatch() -> int:
    return dispatch_pending_digests()
