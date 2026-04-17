from __future__ import annotations

from apps.common.exceptions import ValidationError


def ensure_not_soft_deleted(*, instance, resource: str) -> None:
    if getattr(instance, "deleted_at", None) is not None:
        raise ValidationError(
            f"{resource} is soft-deleted and cannot be accessed.",
            details={"resource": resource},
        )
