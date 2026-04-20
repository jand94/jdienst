from __future__ import annotations

from celery import shared_task

from apps.notification.api.v1.services import (
    build_pending_digests,
    dispatch_pending_deliveries,
    dispatch_pending_digests,
    log_pipeline_event,
)


@shared_task(
    name="notification.dispatch_pending_deliveries",
    autoretry_for=(TimeoutError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def run_notification_delivery_dispatch() -> int:
    dispatched = dispatch_pending_deliveries()
    log_pipeline_event(
        event="notification.task.delivery_dispatch.completed",
        dispatched=dispatched,
    )
    return dispatched


@shared_task(
    name="notification.build_pending_digests",
    autoretry_for=(TimeoutError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def run_notification_digest_build() -> int:
    created = build_pending_digests()
    log_pipeline_event(
        event="notification.task.digest_build.completed",
        created=created,
    )
    return created


@shared_task(
    name="notification.dispatch_pending_digests",
    autoretry_for=(TimeoutError,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 3},
)
def run_notification_digest_dispatch() -> int:
    processed = dispatch_pending_digests()
    log_pipeline_event(
        event="notification.task.digest_dispatch.completed",
        processed=processed,
    )
    return processed
