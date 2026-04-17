from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.api.v1.services import assign_user_to_default_tenant


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def auto_assign_default_tenant_on_user_create(sender, instance, created, **kwargs):
    if not created:
        return
    assign_user_to_default_tenant(
        user=instance,
        actor=instance if getattr(instance, "is_authenticated", False) else None,
        source="signal.user_create",
    )
