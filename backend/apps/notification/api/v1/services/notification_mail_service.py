from __future__ import annotations

import smtplib

from django.conf import settings
from django.core.mail import send_mail

from apps.notification.api.v1.services.notification_observability_service import log_pipeline_event
from apps.notification.models import Notification


class NotificationMailDeliveryError(Exception):
    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason


def classify_mail_exception(exc: Exception) -> tuple[str, bool]:
    if isinstance(exc, smtplib.SMTPRecipientsRefused):
        return "smtp_recipients_refused", False
    if isinstance(exc, smtplib.SMTPSenderRefused):
        return "smtp_sender_refused", False
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        return "smtp_authentication_error", False
    if isinstance(exc, smtplib.SMTPConnectError):
        return "smtp_connect_error", True
    if isinstance(exc, smtplib.SMTPServerDisconnected):
        return "smtp_server_disconnected", True
    if isinstance(exc, smtplib.SMTPDataError):
        return "smtp_data_error", False
    return "smtp_unexpected_error", True


def send_notification_email(*, notification: Notification) -> int:
    recipient = notification.recipient
    if not recipient.email:
        raise NotificationMailDeliveryError(
            reason="recipient_missing_email",
            message="Recipient has no email address.",
        )
    try:
        sent_count = send_mail(
            subject=notification.title,
            message=notification.body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[recipient.email],
            fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001
        reason, retryable = classify_mail_exception(exc)
        log_pipeline_event(
            event="notification.mail.delivery.error",
            notification_id=str(notification.pk),
            recipient_id=str(notification.recipient_id),
            reason=reason,
            retryable=retryable,
            error=str(exc),
        )
        raise NotificationMailDeliveryError(reason=reason, message=str(exc)) from exc
    if sent_count <= 0:
        raise NotificationMailDeliveryError(
            reason="smtp_not_accepted",
            message="SMTP server did not accept the message.",
        )
    log_pipeline_event(
        event="notification.mail.delivery.sent",
        notification_id=str(notification.pk),
        recipient_id=str(notification.recipient_id),
        sent_count=sent_count,
    )
    return sent_count


def send_digest_email(*, recipient_email: str, subject: str, body: str) -> int:
    if not recipient_email:
        raise NotificationMailDeliveryError(
            reason="recipient_missing_email",
            message="Digest recipient has no email address.",
        )
    try:
        sent_count = send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            recipient_list=[recipient_email],
            fail_silently=False,
        )
    except Exception as exc:  # noqa: BLE001
        reason, retryable = classify_mail_exception(exc)
        log_pipeline_event(
            event="notification.mail.digest.error",
            recipient_email=recipient_email,
            reason=reason,
            retryable=retryable,
            error=str(exc),
        )
        raise NotificationMailDeliveryError(reason=reason, message=str(exc)) from exc
    if sent_count <= 0:
        raise NotificationMailDeliveryError(
            reason="smtp_not_accepted",
            message="SMTP server did not accept the digest message.",
        )
    log_pipeline_event(
        event="notification.mail.digest.sent",
        recipient_email=recipient_email,
        sent_count=sent_count,
    )
    return sent_count
