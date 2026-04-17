from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.common"

    def ready(self):
        # Register signal handlers (e.g. optional default-tenant assignment on user creation).
        from apps.common import signals  # noqa: F401
