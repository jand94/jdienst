from django.conf import settings
from django.db import models

from .base_model import TimeStampedModel, UUIDPrimaryKeyModel
from .tenant import Tenant


class TenantMembership(UUIDPrimaryKeyModel, TimeStampedModel):
    ROLE_OWNER = "owner"
    ROLE_ADMIN = "admin"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = (
        (ROLE_OWNER, "Owner"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_MEMBER, "Member"),
    )

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_memberships")
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_MEMBER, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("tenant", "user"),
                name="common_tenant_membership_unique",
            )
        ]
        indexes = [
            models.Index(fields=("tenant", "is_active"), name="common_tmem_tnt_act_idx"),
            models.Index(fields=("user", "is_active"), name="common_tmem_usr_act_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}@{self.tenant_id} ({self.role})"
