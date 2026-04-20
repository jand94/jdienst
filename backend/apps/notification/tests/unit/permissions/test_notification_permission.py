from __future__ import annotations

import pytest
from rest_framework.test import APIRequestFactory

from apps.notification.api.v1.permissions import IsNotificationOperator, IsStaffNotificationWriter


class _DummyView:
    action = "create"


@pytest.mark.django_db
def test_staff_writer_logs_permission_denied_for_non_staff(user, monkeypatch):
    captured = []
    request = APIRequestFactory().post("/api/notification/v1/notifications/")
    request.user = user

    monkeypatch.setattr(
        "apps.notification.api.v1.permissions.notification_api.log_permission_denied",
        lambda **kwargs: captured.append(kwargs),
    )

    allowed = IsStaffNotificationWriter().has_permission(request, _DummyView())

    assert allowed is False
    assert len(captured) == 1
    assert captured[0]["resource"] == "notification.create"


@pytest.mark.django_db
def test_notification_operator_logs_permission_denied_for_non_operator(user, monkeypatch):
    captured = []
    request = APIRequestFactory().get("/api/notification/v1/ops/health-snapshot/")
    request.user = user

    monkeypatch.setattr(
        "apps.notification.api.v1.permissions.notification_api.log_permission_denied",
        lambda **kwargs: captured.append(kwargs),
    )

    allowed = IsNotificationOperator().has_permission(request, _DummyView())

    assert allowed is False
    assert len(captured) == 1
    assert captured[0]["resource"] == "notification.ops.read"
