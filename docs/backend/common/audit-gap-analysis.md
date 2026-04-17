# Audit Gap Analyse (`apps/common`)

## Zweck

Dieses Dokument fasst den aktuellen Audit-Stand gegen ein SOC2/ISO-orientiertes Zielbild zusammen.
Es dient als Entscheidungsgrundlage fuer Architektur, Betrieb und Roadmap.

## Ist-Stand (aktuell umgesetzt)

- Persistentes Audit-Event-Modell mit Kernfeldern (`action`, `target_model`, `target_id`, `actor`, `metadata`, `ip_address`, `user_agent`).
- Integritaetsfelder (`previous_hash`, `integrity_hash`) und append-only Enforcement auf Model-Ebene.
- Service `record_audit_event(...)` mit Pflichtfeld-Validierung und Metadaten-Sanitization.
- Admin-Hooks fuer `admin.create`, `admin.update`, `admin.delete` inklusive Feld-Diffs bei Updates.
- Read-only Audit API mit Permission-Gate (`common.view_auditevent`) und OpenAPI-Dokumentation.
- Operations-Bausteine fuer Archivierung und SIEM-Export (inkl. `archived_at` / `exported_at`).

## Soll-Stand (Enterprise, SOC2/ISO-orientiert)

- Nachvollziehbarkeit sicherheitsrelevanter Ereignisse in allen kritischen Service-Flows.
- Integritaet mit internem tamper-evident Nachweis plus externer Härtung.
- Rollen- und Zugriffsschutz fuer Audit-Lesepfade (Auditor-Prinzip, Least-Privilege, Audit-of-audit).
- Betriebsfaehigkeit mit verbindlicher Retention-Governance, Monitoring, Incident-/Forensik-Prozess.
- Stabiler SIEM-Betriebsprozess mit Evidenzen (nicht nur Exportmechanik).

## Gap-Matrix

| Bereich | Status | Offene Luecke | Prioritaet |
|---|---|---|---|
| Event-Coverage | Teilweise umgesetzt | Kritische Domain-Flows app-weit konsistent auditiert | Hoch |
| Integritaet | Weit umgesetzt | Externer Signatur-/WORM-Nachweis, periodische Verifikation | Mittel |
| Zugriffskontrolle | Teilweise umgesetzt | Auditor-Rollenmodell + Audit-of-audit fuer Lesezugriffe | Hoch |
| Forensik-Kontext | Teilweise umgesetzt | Request-/Trace-Korrelation als Pflichtmetadaten | Mittel |
| Betrieb | Teilweise umgesetzt | Verbindliche Retention-Klassen, Restore-Evidenz, Alert-SLOs | Hoch |
| Externe Nachweisbarkeit | Basis umgesetzt | SIEM-Prozessreife inkl. Runbooks/Kontrollnachweise | Mittel |

## Verbindliche Leitplanken aus `docs/engineering`

- Security/Audit-Anforderungen: `docs/engineering/security.md`
- Service-Layer, Transaktionen, Observability: `docs/engineering/backend.md`
- Testpflicht und Testtiefe: `docs/engineering/testing.md`
- API-/Schema-Vertrag fuer Audit-Endpunkte: `docs/engineering/api.md`

## Abgrenzung

Dieses Dokument beschreibt Architektur- und Governance-Luecken.
Die technische Umsetzung erfolgt phasenweise gemaess `audit-roadmap.md`.

## Kurzfazit

Die Basis ist enterprise-tauglich vorbereitet (Integritaetskette, append-only, read-only API, Export/Archiv-Bausteine).
Der verbleibende Abstand zum Endzustand liegt vor allem in Governance, Betriebsreife und flächiger Event-Coverage.

## Querverweise

- Basisnutzung: `docs/backend/common/audit-basics.md`
- Architektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy: `docs/backend/common/audit-security-privacy.md`
- Betrieb: `docs/backend/common/audit-operations.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
