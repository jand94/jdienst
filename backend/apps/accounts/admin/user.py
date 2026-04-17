from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.common.admin.audit_mixin import AdminAuditTrailMixin
from apps.accounts.models import User


@admin.register(User)
class UserAdmin(AdminAuditTrailMixin, DjangoUserAdmin):
    pass
