# common

## Zweck

`common` stellt wiederverwendbare Backend-Bausteine bereit, damit neue Apps
einheitlich auditierbar implementiert werden koennen.

Der Fokus liegt auf:
- abstrakten Audit-Basismodellen fuer `models/`
- wiederverwendbaren DRF-Serializer-Bausteinen
- standardisierten Admin-Basisklassen
- zentraler Audit-Service-Logik fuer nachvollziehbare Events

## Struktur

- `models/base_model.py`: UUID-PK + Timestamp-Abstraktionen
- `models/audit_fields.py`: abstrakte `created_by`/`updated_by`-Auditfelder
- `models/audit_event.py`: persistente Audit-Events
- `exceptions/audit.py`: fachliche Audit-Exceptions
- `api/v1/services/audit_service.py`: sichere Event-Erzeugung inkl. Metadaten-Sanitization
- `api/v1/serializers/audit.py`: Audit-Serializer und Read-only-Mixin
- `admin/base_admin.py`: wiederverwendbare Admin-Basis
- `admin/audit_event.py`: Admin-Registrierung fuer AuditEvent
- `tests/`: Unit- und Integrationstests inkl. Factories

## Nutzung in neuen Apps

1. Eigene Modelle von `UUIDPrimaryKeyModel` oder `AuditFieldsModel` ableiten.
2. Bei sicherheitsrelevanten Mutationen `record_audit_event(...)` im Service-Layer aufrufen.
3. Bei DRF-Serializern das `AuditReadOnlyFieldsSerializerMixin` fuer Auditfelder nutzen.
4. Admin-Konfigurationen bei Bedarf von `AuditBaseAdmin` ableiten.

## Leitplanken

- Keine sensiblen Daten in `metadata` speichern; sensible Keys werden im Service gefiltert.
- Auditierung gehoert in Services, nicht in Views/Serializer-Logik.
- `__init__.py` nur fuer Re-Exports verwenden.
- Neue Endpunkte weiterhin gemaess `docs/engineering/api.md` schema-dokumentieren.

## Weiterfuehrend

Details und Beispiele: `docs/backend/common/audit-basics.md`.
