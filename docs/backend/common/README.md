# common

## Zweck

`apps/common` ist das zentrale Audit- und Basis-Framework fuer Domain-Apps im Backend.
Es liefert wiederverwendbare Bausteine, damit neue Apps nachvollziehbar, testbar und
gemäss den Engineering-Regeln implementiert werden.

## Garantien (aktueller Stand)

- Persistente Audit-Events fuer protokollierte Aktionen (`AuditEvent`).
- Sanitization sensibler Metadaten beim Schreiben ueber `record_audit_event(...)`.
- Automatische Admin-Auditierung fuer `create`, `update`, `delete` inkl. Feld-Diff bei Updates.
- Wiederverwendbare Model-/Serializer-/Admin-Bausteine fuer konsistente Nutzung in Domain-Apps.

## Nicht-Ziele (aktueller Stand)

- Kein vollstaendiges Immutability-/Tamper-Proof-Modell (z. B. Hash-Kette, WORM-Speicher).
- Kein fertiger SIEM-Exportpfad.
- Keine globale Garantie, dass bereits alle kritischen API-Flows ausserhalb des Admins auditiert sind.

## Struktur

- `models/base_model.py`: UUID-PK + Timestamp-Abstraktionen
- `models/audit_fields.py`: abstrakte `created_by`/`updated_by`-Auditfelder
- `models/audit_event.py`: persistente Audit-Events
- `exceptions/audit.py`: fachliche Audit-Exceptions
- `api/v1/services/audit_service.py`: sichere Event-Erzeugung inkl. Metadaten-Sanitization
- `api/v1/serializers/audit.py`: Audit-Serializer und Read-only-Mixin
- `admin/base_admin.py`: wiederverwendbare Admin-Basis
- `admin/audit_mixin.py`: Audit-Hooks fuer Admin-Aktionen
- `admin/audit_event.py`: Admin-Registrierung fuer AuditEvent
- `tests/`: Unit- und Integrationstests inkl. Factories

## Nutzung in neuen Apps

1. Eigene Modelle von `UUIDPrimaryKeyModel` oder `AuditFieldsModel` ableiten.
2. Bei sicherheitsrelevanten Mutationen `record_audit_event(...)` im Service-Layer aufrufen.
3. Bei DRF-Serializern `AuditReadOnlyFieldsSerializerMixin` fuer Auditfelder nutzen.
4. Admin-Konfigurationen von `AuditBaseAdmin` oder `AdminAuditTrailMixin` ableiten.

## Verbindliche Leitplanken

- Security-/Audit-Regeln: `docs/engineering/security.md`
- Service-/Transaktionsgrenzen: `docs/engineering/backend.md`
- Testpflicht und Testmatrix: `docs/engineering/testing.md`
- API-/OpenAPI-Vertrag bei Audit-Endpunkten: `docs/engineering/api.md`

## Weiterfuehrende Dokumente

- Basisnutzung und Event-Konventionen: `docs/backend/common/audit-basics.md`
- Ist-vs-Soll Gap-Analyse: `docs/backend/common/audit-gap-analysis.md`
- Enterprise-Zielarchitektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy-Standard fuer Auditdaten: `docs/backend/common/audit-security-privacy.md`
- Betrieb (Retention, Monitoring, Incident): `docs/backend/common/audit-operations.md`
- Technischer Ausbauplan: `docs/backend/common/audit-roadmap.md`
