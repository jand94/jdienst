from django.test import override_settings
import pytest

from apps.common.api.v1.services.platform_settings_service import get_platform_settings
from apps.common.exceptions import InfrastructureError


def test_platform_settings_reads_defaults():
    values = get_platform_settings()

    assert values.max_outbox_pending >= 0
    assert values.outbox_max_attempts >= 1


@override_settings(COMMON_OUTBOX_MAX_ATTEMPTS=0)
def test_platform_settings_validates_attempts():
    with pytest.raises(InfrastructureError):
        get_platform_settings()
