"""
Django base settings for backend project.
"""

import os
from pathlib import Path


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str = "") -> list[str]:
    raw_value = os.getenv(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]


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
    "django_filters",
    "drf_spectacular",
]

INTERNAL_APPS: list[str] = [
    # Domain apps are added here as they are introduced.

    "apps.accounts",
    "apps.common",]

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

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "EXCEPTION_HANDLER": "apps.common.api.v1.services.error_mapping_service.api_exception_handler",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "jdienst API",
    "DESCRIPTION": "OpenAPI schema for the jdienst backend.",
    "VERSION": "1.0.0",
}

AUTH_USER_MODEL = "accounts.User"

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
COMMON_IDEMPOTENCY_RETENTION_SECONDS = int(os.getenv("COMMON_IDEMPOTENCY_RETENTION_SECONDS", "86400"))
