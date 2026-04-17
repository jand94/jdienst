# Audit Gap Analyse (`apps/common`)

## Zweck

Dieses Dokument fasst den aktuellen Audit-Stand gegen ein SOC2/ISO-orientiertes Zielbild zusammen.
Es dient als Entscheidungsgrundlage fuer Architektur, Betrieb und Roadmap.

## Ist-Stand (aktuell umgesetzt)

- Persistentes Audit-Event-Modell mit Kernfeldern (`action`, `target_model`, `target_id`, `actor`, `metadata`, `ip_address`, `user_agent`).
- Service `record_audit_event(...)` mit Pflichtfeld-Validierung und Metadaten-Sanitization.
- Admin-Hooks fuer `admin.create`, `admin.update`, `admin.delete` inklusive Feld-Diffs bei Updates.
- Sichtbarkeit von Audit-Events im Django Admin.

## Soll-Stand (Enterprise, SOC2/ISO-orientiert)

- Nachvollziehbarkeit sicherheitsrelevanter Ereignisse nicht nur im Admin, sondern in allen kritischen Service-Flows.
- Integritaetsstrategie fuer Auditdaten (tamper-evident/append-only Entscheidung und Umsetzungspfad).
- Rollen- und Zugriffsschutz fuer Audit-Lesepfade (Auditor-Prinzip, Least-Privilege, Audit-of-audit).
- Betriebsfaehigkeit mit Retention, Archivierung, Monitoring, Incident-/Forensik-Prozess.
- Optionaler API-/SIEM-Zugriff mit dokumentiertem OpenAPI-Vertrag und klaren Permissions.

## Gap-Matrix

| Bereich | Ist | Soll | Prioritaet |
|---|---|---|---|
| Event-Coverage | Schwerpunkt Admin-Aenderungen | Kritische API-/Auth-/Permission-Flows auditieren | Hoch |
| Integritaet | Standard-DB-Objekte ohne Immutability-Garantie | Tamper-evident oder append-only Konzept | Hoch |
| Zugriffskontrolle | Primär Admin-Zugriff | Auditor-Rollen + Objekt-/Use-Case-Policy | Hoch |
| Forensik-Kontext | Basisfelder vorhanden | Korrelation (request/trace), erweiterte Kontextstandards | Mittel |
| Betrieb | Keine formalen Retention-/Archivregeln | Definierte Aufbewahrung, Export, Monitoring | Mittel |
| Externe Nachweisbarkeit | Kein standardisierter SIEM-Pfad | Definierter Export und Betriebsmetriken | Mittel |

## Verbindliche Leitplanken aus `docs/engineering`

- Security/Audit-Anforderungen: `docs/engineering/security.md`
- Service-Layer, Transaktionen, Observability: `docs/engineering/backend.md`
- Testpflicht und Testtiefe: `docs/engineering/testing.md`
- API-/Schema-Vertrag fuer Audit-Endpunkte: `docs/engineering/api.md`

## Abgrenzung

Dieses Dokument beschreibt Architektur- und Governance-Luecken.
Die technische Umsetzung erfolgt phasenweise gemaess `audit-roadmap.md`.

## Querverweise

- Basisnutzung: `docs/backend/common/audit-basics.md`
- Architektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy: `docs/backend/common/audit-security-privacy.md`
- Betrieb: `docs/backend/common/audit-operations.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
