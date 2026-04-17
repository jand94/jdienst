# Audit Basics (`apps/common`)

## Ziel

Einheitliche, nachvollziehbare Auditierung fuer alle kuenftigen Domain-Apps.

## Verfuegbare Bausteine

### Modelle

- `UUIDPrimaryKeyModel`: UUID als Primary Key.
- `TimeStampedModel`: `created_at` / `updated_at`.
- `AuditFieldsModel`: `created_by` / `updated_by` zusaetzlich zu Timestamps.
- `AuditEvent`: persistente Audit-Events fuer sicherheitsrelevante Aktionen mit
  `previous_hash`, `integrity_hash`, `archived_at`, `exported_at`.

### Services

- `record_audit_event(...)` in `apps.common.api.v1.services.audit_service`
  - validiert Pflichtfelder (`action`, `target_model`, `target_id`)
  - sanitisiert Metadaten rekursiv
  - entfernt sensible Keys (z. B. `password`, `token`, `authorization`)
  - erzeugt Integritaetskette (`previous_hash` -> `integrity_hash`)

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
- `AuditEventSerializer`: read-only Standardserializer fuer `AuditEvent`.

### API / Permissions

- `AuditEventViewSet`: read-only List/Detail API mit Filter/Pagination.
- `IsAuditReader`: Zugriff nur fuer Superuser oder `common.view_auditevent`.
- `AuditOperationsViewSet`: Operator-Endpunkte fuer Verify/Health/Export-Preview/Archive/Role-Sync.
- `IsAuditOperator`: Zugriff fuer Superuser oder Staff mit Audit-Reader-Rechten.

### Admin

- `AuditBaseAdmin`: gemeinsame readonly-/ordering-Konvention.
- `AuditEventAdmin`: Admin-Ansicht fuer AuditEvent-Eintraege.
- `AdminAuditTrailMixin`: erzeugt automatisch `admin.create`, `admin.update`, `admin.delete`.

### Operations

- `archive_old_events(...)`: markiert alte Events als archiviert (`archived_at`).
- `build_siem_payload(...)`: standardisierte Exportstruktur.
- `mark_events_exported(...)`: markiert exportierte Events (`exported_at`).
- Management Commands:
  - `python manage.py audit_archive_events --before-days <n>`
  - `python manage.py audit_archive_events --use-retention-policy`
  - `python manage.py audit_export_siem --limit <n> [--mark-exported]`
  - `python manage.py audit_verify_integrity [--create-checkpoint]`
  - `python manage.py audit_health_snapshot --window-hours <n>`
  - `python manage.py audit_setup_roles`

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

- Kein externer, kryptographisch signierter Integritaetsnachweis (z. B. KMS-Signatur/WORM).
- Kein vollstaendiges Audit-of-audit fuer alle Lesezugriffe.
- SIEM-Exportpfad ist funktional vorhanden, aber Betriebsreife (SLO/Alerts/Playbooks) ist noch auszubauen.
- Vollstaendige Event-Coverage ausserhalb des Admins muss pro Domain-Service weiterhin explizit umgesetzt werden.

## Weiterfuehrend

- Architektur und Vertrauensmodell: `docs/backend/common/audit-architecture.md`
- Security/Privacy-Regeln: `docs/backend/common/audit-security-privacy.md`
- Betrieb und Retention: `docs/backend/common/audit-operations.md`
- Engineering Security: `docs/engineering/security.md`
- Engineering Backend: `docs/engineering/backend.md`
- Engineering Testing: `docs/engineering/testing.md`
- Engineering API: `docs/engineering/api.md`
