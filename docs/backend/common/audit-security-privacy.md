# Audit Security & Privacy (`apps/common`)

## Zweck

Dieses Dokument definiert Security- und Privacy-Standards fuer Auditdaten im Sinne
eines SOC2/ISO-orientierten Betriebs.

## Sicherheitsprinzipien

- Auditdaten sind sicherheitsrelevant und muessen vor unautorisiertem Zugriff geschuetzt werden.
- Audit-Events duerfen keine Secrets enthalten.
- Zugriff auf Audit-Events folgt Least-Privilege und expliziten Berechtigungen.

## Metadaten-Hygiene

Pflicht:

- Nur notwendige Kontexte in `metadata` speichern.
- Keine sensiblen Rohwerte loggen (Token, Passwoerter, Secrets, API-Keys).
- Nutzung der zentralen Sanitization ueber `record_audit_event(...)`.

Verboten:

- Ungefilterte Request-Bodies oder Header vollständig in Auditdaten.
- personenbezogene Daten ohne klaren Zweck und Minimierung.

## Zugriffskontrolle

### Aktueller Stand

- Lesbarkeit primär ueber Django Admin mit staff/superuser Kontext.

### Zielbild

- Dedizierte Auditor-Rollen.
- Read-only Zugriff fuer Audit-Reader.
- Objekt-/Use-Case-basierte Permissions bei API-Exposition.
- Audit-of-audit: Zugriffe auf Auditdaten sollen selbst nachvollziehbar sein.

## Privacy- und Compliance-Hinweise

- Datenminimierung strikt anwenden.
- Aufbewahrung nur so lange wie notwendig (siehe `audit-operations.md`).
- Bei regulatorischen Anforderungen (z. B. DSGVO-Löschkontext) Widersprueche zwischen
  Nachweispflicht und Loeschpflicht fachlich dokumentieren.

## Netzwerk- und Kontextdaten

- `ip_address` und `user_agent` nur als notwendiger Sicherheitskontext.
- In Proxy-Setups muss die vertrauenswuerdige Ermittlung der Client-IP dokumentiert sein.
- spaeter: `request_id`/`trace_id` fuer forensische Korrelation standardisieren.

## Verifikation (Pflicht fuer Aenderungen)

- Unit-/Integrationstests fuer Sanitization und Permission-Grenzen.
- Tests fuer unzulaessige Zugriffe auf Audit-Lesepfade.
- Bei API-Endpunkten: OpenAPI- und API-Testpflicht nach `docs/engineering/api.md`
  und `docs/engineering/testing.md`.

## Querverweise

- Architektur: `docs/backend/common/audit-architecture.md`
- Betrieb: `docs/backend/common/audit-operations.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
- Engineering Security: `docs/engineering/security.md`
