from apps.common.api.v1.services.platform_health_service import _collect_notification_snapshot


def test_collect_notification_snapshot_reports_degraded_on_import_failure(monkeypatch):
    def _raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "apps.notification.api.v1.services.notification_health_service.collect_notification_health_snapshot",
        _raise_error,
    )

    snapshot = _collect_notification_snapshot(window_hours=24)

    assert snapshot is not None
    assert snapshot["status"] == "degraded"
    assert snapshot["error_class"] == "RuntimeError"
