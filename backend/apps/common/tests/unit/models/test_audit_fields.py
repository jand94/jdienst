from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from apps.common.models import AuditEvent, AuditFieldsModel, UUIDPrimaryKeyModel


def test_uuid_primary_key_model_exposes_uuid_id():
    id_field = UUIDPrimaryKeyModel._meta.get_field("id")

    assert isinstance(id_field, models.UUIDField)
    assert id_field.primary_key is True


def test_audit_fields_model_tracks_actor_fields():
    created_by = AuditFieldsModel._meta.get_field("created_by")
    updated_by = AuditFieldsModel._meta.get_field("updated_by")

    assert created_by.remote_field.model == settings.AUTH_USER_MODEL
    assert updated_by.remote_field.model == settings.AUTH_USER_MODEL
    assert created_by.null is True
    assert updated_by.null is True


def test_audit_event_contains_required_audit_dimensions():
    actor_field = AuditEvent._meta.get_field("actor")
    metadata_field = AuditEvent._meta.get_field("metadata")

    assert actor_field.remote_field.model is get_user_model()
    assert isinstance(metadata_field, models.JSONField)
    assert metadata_field.default == dict

    action_field = AuditEvent._meta.get_field("action")
    target_model_field = AuditEvent._meta.get_field("target_model")
    target_id_field = AuditEvent._meta.get_field("target_id")

    assert action_field.max_length == 128
    assert target_model_field.max_length == 128
    assert target_id_field.max_length == 64
