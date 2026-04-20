"""
Django base settings for backend project.
"""

import os
from datetime import timedelta
from pathlib import Path

from corsheaders.defaults import default_headers


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str = "") -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _env_optional(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-local-dev-key-change-me",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _env_bool("DEBUG", default=True)

ALLOWED_HOSTS = _env_list(
    "ALLOWED_HOSTS",
    default="localhost,127.0.0.1,backend",
)

CSRF_TRUSTED_ORIGINS = _env_list(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
)


# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
    "channels",
]

INTERNAL_APPS: list[str] = [
    # Domain apps are added here as they are introduced.

    "apps.accounts",
    "apps.common",
    "apps.auth",
    "apps.notification",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + INTERNAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "apps.common.middleware.tenant_context.TenantContextMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.common.middleware.request_context.CommonRequestContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"


# Database
DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").lower()

if DB_ENGINE == "postgres":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "app"),
            "USER": os.getenv("POSTGRES_USER", "app"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "app"),
            "HOST": os.getenv("POSTGRES_HOST", "db"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

CORS_ALLOWED_ORIGINS = _env_list(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://127.0.0.1:3000",
)
CORS_ALLOW_CREDENTIALS = _env_bool("CORS_ALLOW_CREDENTIALS", default=True)
CORS_ALLOW_HEADERS = [*default_headers, "x-tenant-slug"]

AUTH_API_ENABLE_SESSION_AUTH = _env_bool("AUTH_API_ENABLE_SESSION_AUTH", default=True)
AUTH_JWT_ALGORITHM = os.getenv("AUTH_JWT_ALGORITHM", "HS256")
AUTH_JWT_SIGNING_KEY = _env_optional("AUTH_JWT_SIGNING_KEY") or SECRET_KEY
AUTH_JWT_VERIFYING_KEY = _env_optional("AUTH_JWT_VERIFYING_KEY")
AUTH_JWT_AUDIENCE = _env_optional("AUTH_JWT_AUDIENCE")
AUTH_JWT_ISSUER = _env_optional("AUTH_JWT_ISSUER")
AUTH_JWT_JWK_URL = _env_optional("AUTH_JWT_JWK_URL")

_default_authentication_classes = [
    "rest_framework_simplejwt.authentication.JWTAuthentication",
]
if AUTH_API_ENABLE_SESSION_AUTH:
    _default_authentication_classes.append("rest_framework.authentication.SessionAuthentication")

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": _default_authentication_classes,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "auth_login": os.getenv("AUTH_LOGIN_RATE", "10/minute"),
        "auth_refresh": os.getenv("AUTH_REFRESH_RATE", "30/hour"),
        "auth_logout": os.getenv("AUTH_LOGOUT_RATE", "60/hour"),
        "notification_create": os.getenv("NOTIFICATION_CREATE_RATE", "120/hour"),
        "notification_mark_read": os.getenv("NOTIFICATION_MARK_READ_RATE", "240/hour"),
        "notification_bulk_mark_read": os.getenv("NOTIFICATION_BULK_MARK_READ_RATE", "60/hour"),
        "notification_preference_update": os.getenv("NOTIFICATION_PREFERENCE_UPDATE_RATE", "120/hour"),
        "notification_ops_snapshot": os.getenv("NOTIFICATION_OPS_SNAPSHOT_RATE", "120/hour"),
    },
    "EXCEPTION_HANDLER": "apps.common.api.v1.services.error_mapping_service.api_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "jdienst API",
    "DESCRIPTION": "OpenAPI schema for the jdienst backend.",
    "VERSION": "1.0.0",
    "ENUM_NAME_OVERRIDES": {
        "NotificationChannelEnum": [
            ("in_app", "In-App"),
            ("email", "Email"),
            ("realtime", "Realtime"),
            ("digest", "Digest"),
        ],
        "NotificationStatusEnum": [
            ("unread", "Unread"),
            ("read", "Read"),
            ("archived", "Archived"),
        ],
        "NotificationDeliveryStatusEnum": [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("failed", "Failed"),
            ("skipped", "Skipped"),
        ],
        "NotificationDigestStatusEnum": [
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("failed", "Failed"),
        ],
        "TenantStatusEnum": [
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("archived", "Archived"),
        ],
    },
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
}

AUTH_USER_MODEL = "accounts.User"

AUTH_ACCESS_TOKEN_LIFETIME_MINUTES = _env_int("AUTH_ACCESS_TOKEN_LIFETIME_MINUTES", 10)
AUTH_REFRESH_TOKEN_LIFETIME_DAYS = _env_int("AUTH_REFRESH_TOKEN_LIFETIME_DAYS", 14)
AUTH_REFRESH_COOKIE_NAME = os.getenv("AUTH_REFRESH_COOKIE_NAME", "refresh_token")
AUTH_REFRESH_COOKIE_SECURE = _env_bool("AUTH_REFRESH_COOKIE_SECURE", default=True)
AUTH_REFRESH_COOKIE_HTTPONLY = _env_bool("AUTH_REFRESH_COOKIE_HTTPONLY", default=True)
AUTH_REFRESH_COOKIE_SAMESITE = os.getenv("AUTH_REFRESH_COOKIE_SAMESITE", "Lax")
AUTH_REFRESH_COOKIE_DOMAIN = os.getenv("AUTH_REFRESH_COOKIE_DOMAIN", None)
AUTH_REFRESH_COOKIE_PATH = os.getenv("AUTH_REFRESH_COOKIE_PATH", "/api/auth/")
AUTH_REFRESH_COOKIE_MAX_AGE_SECONDS = _env_int(
    "AUTH_REFRESH_COOKIE_MAX_AGE_SECONDS",
    AUTH_REFRESH_TOKEN_LIFETIME_DAYS * 24 * 60 * 60,
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=AUTH_ACCESS_TOKEN_LIFETIME_MINUTES),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=AUTH_REFRESH_TOKEN_LIFETIME_DAYS),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": AUTH_JWT_ALGORITHM,
    "SIGNING_KEY": AUTH_JWT_SIGNING_KEY,
    "VERIFYING_KEY": AUTH_JWT_VERIFYING_KEY,
    "AUDIENCE": AUTH_JWT_AUDIENCE,
    "ISSUER": AUTH_JWT_ISSUER,
    "JWK_URL": AUTH_JWT_JWK_URL,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

AUDIT_READER_GROUPS = _env_list("AUDIT_READER_GROUPS", default="AuditReader")
AUDIT_INTEGRITY_SIGNING_KEY = os.getenv("AUDIT_INTEGRITY_SIGNING_KEY", SECRET_KEY)
COMMON_OUTBOX_MAX_ATTEMPTS = int(os.getenv("COMMON_OUTBOX_MAX_ATTEMPTS", "10"))
COMMON_PLATFORM_MAX_OUTBOX_PENDING = int(os.getenv("COMMON_PLATFORM_MAX_OUTBOX_PENDING", "5000"))
COMMON_PLATFORM_MAX_OUTBOX_OLDEST_AGE_SECONDS = int(
    os.getenv("COMMON_PLATFORM_MAX_OUTBOX_OLDEST_AGE_SECONDS", "900")
)
COMMON_PLATFORM_MAX_AUDIT_VERIFICATION_AGE_HOURS = int(
    os.getenv("COMMON_PLATFORM_MAX_AUDIT_VERIFICATION_AGE_HOURS", "24")
)
COMMON_TENANT_HEADER_REQUIRED = _env_bool("COMMON_TENANT_HEADER_REQUIRED", default=True)
COMMON_TENANT_DEFAULT_SLUG = os.getenv("COMMON_TENANT_DEFAULT_SLUG", "")
COMMON_TENANT_AUTO_RESOLVE_SINGLE_MEMBERSHIP = _env_bool(
    "COMMON_TENANT_AUTO_RESOLVE_SINGLE_MEMBERSHIP",
    default=False,
)
COMMON_TENANT_AUTO_ASSIGN_ON_USER_CREATE = _env_bool("COMMON_TENANT_AUTO_ASSIGN_ON_USER_CREATE", default=False)
COMMON_TENANT_DEFAULT_ROLE = os.getenv("COMMON_TENANT_DEFAULT_ROLE", "member")
COMMON_IDEMPOTENCY_RETENTION_SECONDS = int(os.getenv("COMMON_IDEMPOTENCY_RETENTION_SECONDS", "86400"))

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
EMAIL_HOST = os.getenv("EMAIL_HOST", "localhost")
EMAIL_PORT = _env_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = _env_bool("EMAIL_USE_TLS", default=False)
EMAIL_USE_SSL = _env_bool("EMAIL_USE_SSL", default=False)
EMAIL_HOST_USER = _env_optional("EMAIL_HOST_USER") or ""
EMAIL_HOST_PASSWORD = _env_optional("EMAIL_HOST_PASSWORD") or ""
EMAIL_TIMEOUT = _env_int("EMAIL_TIMEOUT", 10)
TEST_RESULTS_EMAIL_ENABLED = _env_bool("TEST_RESULTS_EMAIL_ENABLED", default=True)
TEST_RESULTS_EMAIL_RECIPIENTS = _env_list(
    "TEST_RESULTS_EMAIL_RECIPIENTS",
    default="jdienst@beckerccc.com",
)
TEST_RESULTS_EMAIL_SUBJECT_PREFIX = os.getenv("TEST_RESULTS_EMAIL_SUBJECT_PREFIX", "[pytest]")
TEST_RESULTS_EMAIL_BRANCH = _env_optional("TEST_RESULTS_EMAIL_BRANCH")
TEST_RESULTS_EMAIL_COMMIT = _env_optional("TEST_RESULTS_EMAIL_COMMIT")
TEST_RESULTS_EMAIL_FAIL_ON_TRANSPORT_ERROR = _env_bool("TEST_RESULTS_EMAIL_FAIL_ON_TRANSPORT_ERROR", default=False)

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", CELERY_BROKER_URL)
CELERY_TASK_ALWAYS_EAGER = _env_bool("CELERY_TASK_ALWAYS_EAGER", default=False)
CELERY_TASK_EAGER_PROPAGATES = _env_bool("CELERY_TASK_EAGER_PROPAGATES", default=False)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULE = {
    "notification-dispatch-deliveries": {
        "task": "notification.dispatch_pending_deliveries",
        "schedule": int(os.getenv("NOTIFICATION_DELIVERY_CRON_SECONDS", "15")),
    },
    "notification-build-digests": {
        "task": "notification.build_pending_digests",
        "schedule": int(os.getenv("NOTIFICATION_DIGEST_BUILD_CRON_SECONDS", "300")),
    },
    "notification-dispatch-digests": {
        "task": "notification.dispatch_pending_digests",
        "schedule": int(os.getenv("NOTIFICATION_DIGEST_DISPATCH_CRON_SECONDS", "300")),
    },
}

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [REDIS_URL],
        },
    }
}

NOTIFICATION_DIGEST_WINDOW_MINUTES = _env_int("NOTIFICATION_DIGEST_WINDOW_MINUTES", 60)
NOTIFICATION_DISPATCH_ON_CREATE = _env_bool("NOTIFICATION_DISPATCH_ON_CREATE", default=False)
NOTIFICATION_MAX_DELIVERY_ATTEMPTS = _env_int("NOTIFICATION_MAX_DELIVERY_ATTEMPTS", 5)
NOTIFICATION_RETRY_BASE_SECONDS = _env_int("NOTIFICATION_RETRY_BASE_SECONDS", 60)
NOTIFICATION_HEALTH_MAX_PENDING_DELIVERIES = _env_int("NOTIFICATION_HEALTH_MAX_PENDING_DELIVERIES", 1000)
NOTIFICATION_HEALTH_MAX_OLDEST_PENDING_AGE_SECONDS = _env_int(
    "NOTIFICATION_HEALTH_MAX_OLDEST_PENDING_AGE_SECONDS",
    900,
)
