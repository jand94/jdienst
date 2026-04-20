from __future__ import annotations

import json
from io import StringIO

import pytest
from django.core.management import call_command

from apps.common.models import TenantMembership
from apps.notification.models import Notification, NotificationType


@pytest.mark.django_db
def test_notification_seed_fixture_creates_seed_data(user, tenant):
    stdout = StringIO()

    call_command(
        "notification_seed_fixture",
        tenant_slug=tenant.slug,
        user_email=user.email,
        stdout=stdout,
    )

    assert NotificationType.objects.filter(key="system-alert").exists()
    assert Notification.objects.filter(tenant=tenant, recipient=user).count() >= 1
    assert TenantMembership.objects.filter(tenant=tenant, user=user, is_active=True).exists()


@pytest.mark.django_db
def test_notification_health_snapshot_command_prints_json():
    stdout = StringIO()

    call_command("notification_health_snapshot", window_hours=24, stdout=stdout)
    payload = json.loads(stdout.getvalue())

    assert "delivery" in payload
    assert "digest" in payload
