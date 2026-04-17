# Audit Basics (`apps/common`)

## Ziel

Einheitliche, nachvollziehbare Auditierung fuer alle kuenftigen Domain-Apps.

## Verfuegbare Bausteine

### Modelle

- `UUIDPrimaryKeyModel`: UUID als Primary Key.
- `TimeStampedModel`: `created_at` / `updated_at`.
- `AuditFieldsModel`: `created_by` / `updated_by` zusaetzlich zu Timestamps.
- `AuditEvent`: persistente Audit-Events fuer sicherheitsrelevante Aktionen.

### Services

- `record_audit_event(...)` in `apps.common.api.v1.services.audit_service`
  - validiert Pflichtfelder (`action`, `target_model`, `target_id`)
  - sanitisiert Metadaten rekursiv
  - entfernt sensible Keys (z. B. `password`, `token`, `authorization`)

### Serializer

- `AuditReadOnlyFieldsSerializerMixin`: markiert Auditfelder als read-only.
- `AuditEventSerializer`: Standardserializer fuer `AuditEvent`.

### Admin

- `AuditBaseAdmin`: gemeinsame readonly-/ordering-Konvention.
- `AuditEventAdmin`: Admin-Ansicht fuer AuditEvent-Eintraege.

## Beispiel: Auditierbares Domain-Model

```python
from django.db import models

from apps.common.models import AuditFieldsModel, UUIDPrimaryKeyModel


class Project(UUIDPrimaryKeyModel, AuditFieldsModel):
    name = models.CharField(max_length=255)
```

## Beispiel: Event im Service protokollieren

```python
from apps.common.api.v1.services import record_audit_event


def update_project(*, actor, project, new_name):
    project.name = new_name
    project.updated_by = actor
    project.save(update_fields=["name", "updated_by", "updated_at"])

    record_audit_event(
        action="project.updated",
        target_model="projects.Project",
        target_id=str(project.pk),
        actor=actor,
        metadata={"new_name": new_name},
    )
```

## Sicherheitsnotizen

- Keine Tokens/Passwoerter in Audit-Metadaten loggen.
- Nur business-relevante, minimale Eventdaten speichern.
- Aufruf immer im Service-Layer, nicht verteilt ueber Views.
