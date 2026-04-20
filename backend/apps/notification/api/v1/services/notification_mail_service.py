from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from apps.notification.models import Notification


def send_notification_email(*, notification: Notification) -> int:
    recipient = notification.recipient
    if not recipient.email:
        return 0
    return send_mail(
        subject=notification.title,
        message=notification.body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[recipient.email],
        fail_silently=False,
    )


def send_digest_email(*, recipient_email: str, subject: str, body: str) -> int:
    if not recipient_email:
        return 0
    return send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
        recipient_list=[recipient_email],
        fail_silently=False,
    )
