from django.conf import settings
from django.contrib.auth import get_user_model


def test_auth_user_model_points_to_accounts_user():
    assert settings.AUTH_USER_MODEL == "accounts.User"


def test_get_user_model_returns_accounts_user():
    user_model = get_user_model()

    assert user_model.__name__ == "User"
    assert user_model.__module__ == "apps.accounts.models.user"
