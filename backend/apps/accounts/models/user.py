from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Projektweites User-Modell als stabile Basis für Audit-Referenzen."""

