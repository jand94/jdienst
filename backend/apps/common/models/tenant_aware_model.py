from django.db import models

from .tenant import Tenant


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        abstract = True
