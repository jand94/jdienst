import pytest
from drf_spectacular.generators import SchemaGenerator


@pytest.mark.django_db
def test_notification_schema_tags_paths_and_error_contract():
    schema = SchemaGenerator().get_schema(request=None, public=True)
    paths = schema["paths"]

    notification_list_path = "/api/notification/v1/notifications/"
    notification_mark_read_path = "/api/notification/v1/notifications/{id}/mark-read/"
    notification_bulk_mark_read_path = "/api/notification/v1/notifications/bulk-mark-read/"
    preference_path = "/api/notification/v1/preferences/"
    ops_health_snapshot_path = "/api/notification/v1/ops/health-snapshot/"

    assert notification_list_path in paths
    assert notification_mark_read_path in paths
    assert notification_bulk_mark_read_path in paths
    assert preference_path in paths
    assert ops_health_snapshot_path in paths

    assert paths[notification_list_path]["get"]["tags"] == ["Notification - Inbox"]
    assert paths[notification_mark_read_path]["post"]["tags"] == ["Notification - Inbox - State"]
    assert paths[notification_bulk_mark_read_path]["post"]["tags"] == ["Notification - Inbox - State"]
    assert paths[preference_path]["get"]["tags"] == ["Notification - Preferences"]
    assert paths[ops_health_snapshot_path]["get"]["tags"] == ["Notification - Operations - Health"]

    create_responses = paths[notification_list_path]["post"]["responses"]
    assert create_responses["400"]["content"]["application/json"]["schema"]["$ref"].endswith("/ApiErrorResponse")
    assert create_responses["429"]["content"]["application/json"]["schema"]["$ref"].endswith("/ApiErrorResponse")

    preference_create_responses = paths[preference_path]["post"]["responses"]
    assert preference_create_responses["404"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/ApiErrorResponse"
    )

    mark_read_responses = paths[notification_mark_read_path]["post"]["responses"]
    assert mark_read_responses["404"]["content"]["application/json"]["schema"]["$ref"].endswith("/ApiErrorResponse")
