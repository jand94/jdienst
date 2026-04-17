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

### Event-Konventionen (Pflicht fuer neue Events)

- `action`: `<domain>.<verb>` oder `admin.<verb>` (Beispiele: `invoice.approved`, `admin.update`)
- `target_model`: Django Label-Format, z. B. `accounts.User`
- `target_id`: technische Primärschlüssel-Repräsentation als String
- `metadata.source`: Quelle des Events (`django-admin`, `api`, `task`, `system`)
- `metadata.changes`: bei Updates Feld-Diff im Format:
  - `"field_name": {"old": <wert>, "new": <wert>}`
- keine sensitiven Rohdaten in `metadata` (Tokens, Passwoerter, Secrets)

### Serializer

- `AuditReadOnlyFieldsSerializerMixin`: markiert Auditfelder als read-only.
- `AuditEventSerializer`: Standardserializer fuer `AuditEvent`.

### Admin

- `AuditBaseAdmin`: gemeinsame readonly-/ordering-Konvention.
- `AuditEventAdmin`: Admin-Ansicht fuer AuditEvent-Eintraege.
- `AdminAuditTrailMixin`: erzeugt automatisch `admin.create`, `admin.update`, `admin.delete`.

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
        metadata={
            "source": "api",
            "changes": {"name": {"old": "Alt", "new": new_name}},
        },
    )
```

## Beispiel: Change-Diff lesen

Bei einem `admin.update` Event enthaelt `metadata` typischerweise:

```json
{
  "source": "django-admin",
  "model_name": "user",
  "changes": {
    "first_name": {
      "old": "",
      "new": "Changed"
    }
  }
}
```

## Sicherheitsnotizen

- Keine Tokens/Passwoerter in Audit-Metadaten loggen.
- Nur business-relevante, minimale Eventdaten speichern.
- Aufruf immer im Service-Layer, nicht verteilt ueber Views.
- Bei API-Exposition von Auditdaten sind explizite Permissions und OpenAPI-Dokumentation Pflicht.

## Grenzen (aktuell)

- Keine tamper-evident/append-only Garantie im aktuellen Datenmodell.
- Kein out-of-the-box SIEM-Export.
- Vollstaendige Event-Coverage ausserhalb des Admins muss pro Domain-Service explizit umgesetzt werden.

## Weiterfuehrend

- Architektur und Vertrauensmodell: `docs/backend/common/audit-architecture.md`
- Security/Privacy-Regeln: `docs/backend/common/audit-security-privacy.md`
- Betrieb und Retention: `docs/backend/common/audit-operations.md`
