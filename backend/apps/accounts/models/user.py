from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Projektweites User-Modell als stabile Basis für Audit-Referenzen."""

    navigation_favorites = models.JSONField(default=list, blank=True)

