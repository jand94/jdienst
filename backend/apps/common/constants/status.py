from django.db import models


class PlatformStatus(models.TextChoices):
    OK = "ok", "OK"
    WARNING = "warning", "Warning"
    FAILED = "failed", "Failed"
