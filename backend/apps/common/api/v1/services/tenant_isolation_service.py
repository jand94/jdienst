from __future__ import annotations

from django.db.models import QuerySet

from apps.common.exceptions import InfrastructureError


def tenant_scoped_queryset(*, queryset: QuerySet, tenant, field_name: str = "tenant") -> QuerySet:
    model_field_names = {field.name for field in queryset.model._meta.get_fields()}
    if field_name not in model_field_names:
        raise InfrastructureError(
            f"Model {queryset.model.__name__} does not expose tenant field '{field_name}'.",
        )
    return queryset.filter(**{field_name: tenant})
