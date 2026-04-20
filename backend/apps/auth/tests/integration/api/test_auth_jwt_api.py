import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.models import AuditEvent
from apps.common.tests.factories import TenantFactory, TenantMembershipFactory


@pytest.mark.django_db
def test_login_returns_access_and_sets_refresh_cookie(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-user",
        email="jwt-user@example.com",
        password="SafePass123!",
    )

    response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "SafePass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert response.data["token_type"] == "Bearer"
    assert "refresh_token" not in response.data

    cookie = response.cookies.get("refresh_token")
    assert cookie is not None
    assert cookie.value
    assert cookie["httponly"]
    assert cookie["samesite"]

    assert AuditEvent.objects.filter(
        action="auth.login.succeeded",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).exists()


@pytest.mark.django_db
def test_login_with_invalid_credentials_returns_401_and_logs_failed_attempt(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-user-fail",
        email="jwt-user-fail@example.com",
        password="SafePass123!",
    )

    response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "wrong-password"},
        format="json",
    )

    assert response.status_code == 401
    assert response.data["error"]["code"] == "authentication_failed"

    event = AuditEvent.objects.filter(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).first()
    assert event is not None
    assert "password" not in event.metadata
    assert "refresh_token" not in event.metadata


@pytest.mark.django_db
def test_login_accepts_email_as_identifier(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-email-login",
        email="jwt-email-login@example.com",
        password="SafePass123!",
    )

    response = api_client.post(
        reverse("auth-login"),
        data={"username": user.email, "password": "SafePass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_login_succeeds_without_csrf_even_with_existing_session_cookie():
    user_model = get_user_model()
    session_user_password = "SafePass123!"
    session_user = user_model.objects.create_user(
        username="jwt-session-user",
        email="jwt-session-user@example.com",
        password=session_user_password,
    )
    target_user = user_model.objects.create_user(
        username="jwt-target-user",
        email="jwt-target-user@example.com",
        password="SafePass123!",
    )
    client = APIClient(enforce_csrf_checks=True)
    assert client.login(username=session_user.username, password=session_user_password)

    response = client.post(
        reverse("auth-login"),
        data={"username": target_user.username, "password": "SafePass123!"},
        format="json",
    )

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.django_db
def test_login_with_inactive_user_returns_401_and_audits_failure(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-inactive",
        email="jwt-inactive@example.com",
        password="SafePass123!",
        is_active=False,
    )

    response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "SafePass123!"},
        format="json",
        HTTP_USER_AGENT="jwt-test-agent",
        HTTP_X_FORWARDED_FOR="203.0.113.10",
    )

    assert response.status_code == 401
    event = AuditEvent.objects.filter(
        action="auth.login.failed",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).first()
    assert event is not None
    assert event.metadata["reason"] == "inactive_user"
    assert event.user_agent == "jwt-test-agent"
    assert event.ip_address == "203.0.113.10"


@pytest.mark.django_db
def test_refresh_rotates_refresh_cookie_and_rejects_previous_token(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-user-refresh",
        email="jwt-user-refresh@example.com",
        password="SafePass123!",
    )
    login_response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "SafePass123!"},
        format="json",
    )
    first_refresh = login_response.cookies["refresh_token"].value

    first_refresh_response = api_client.post(reverse("auth-refresh"))
    assert first_refresh_response.status_code == 200
    assert "access" in first_refresh_response.data
    second_refresh = first_refresh_response.cookies["refresh_token"].value
    assert second_refresh
    assert second_refresh != first_refresh

    api_client.cookies["refresh_token"] = first_refresh
    replay_response = api_client.post(reverse("auth-refresh"))
    assert replay_response.status_code == 401
    assert replay_response.data["error"]["code"] == "authentication_failed"
    refresh_success_event = AuditEvent.objects.filter(
        action="auth.refresh.succeeded",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).first()
    assert refresh_success_event is not None


@pytest.mark.django_db
def test_logout_blacklists_refresh_cookie_and_clears_cookie(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-user-logout",
        email="jwt-user-logout@example.com",
        password="SafePass123!",
    )
    login_response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "SafePass123!"},
        format="json",
    )
    access = login_response.data["access"]

    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    logout_response = api_client.post(reverse("auth-logout"))

    assert logout_response.status_code == 200
    cookie = logout_response.cookies.get("refresh_token")
    assert cookie is not None
    assert cookie.value == ""

    refresh_response = api_client.post(reverse("auth-refresh"))
    assert refresh_response.status_code == 401
    assert refresh_response.data["error"]["code"] == "authentication_failed"
    assert AuditEvent.objects.filter(
        action="auth.logout.succeeded",
        target_model="accounts.User",
        target_id=str(user.pk),
    ).exists()


@pytest.mark.django_db
def test_logout_rejects_refresh_token_for_different_user(api_client):
    user_a = get_user_model().objects.create_user(
        username="jwt-logout-a",
        email="jwt-logout-a@example.com",
        password="SafePass123!",
    )
    user_b = get_user_model().objects.create_user(
        username="jwt-logout-b",
        email="jwt-logout-b@example.com",
        password="SafePass123!",
    )

    login_user_a = api_client.post(
        reverse("auth-login"),
        data={"username": user_a.username, "password": "SafePass123!"},
        format="json",
    )
    access_user_a = login_user_a.data["access"]
    api_client.post(
        reverse("auth-login"),
        data={"username": user_b.username, "password": "SafePass123!"},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_user_a}")

    response = api_client.post(reverse("auth-logout"))

    assert response.status_code == 401
    assert response.data["error"]["code"] == "authentication_failed"
    failed_event = AuditEvent.objects.filter(
        action="auth.logout.failed",
        target_model="accounts.User",
        target_id=str(user_a.pk),
    ).first()
    assert failed_event is not None
    assert failed_event.metadata["reason"] == "token_user_mismatch"


@pytest.mark.django_db
def test_access_token_authenticates_existing_protected_accounts_endpoint(api_client):
    user = get_user_model().objects.create_user(
        username="jwt-user-protected",
        email="jwt-user-protected@example.com",
        password="SafePass123!",
    )
    tenant = TenantFactory()
    TenantMembershipFactory(user=user, tenant=tenant)
    login_response = api_client.post(
        reverse("auth-login"),
        data={"username": user.username, "password": "SafePass123!"},
        format="json",
    )
    access = login_response.data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    response = api_client.get(reverse("accounts-user-me"), HTTP_X_TENANT_SLUG=tenant.slug)

    assert response.status_code == 200
    assert response.data["id"] == user.id
