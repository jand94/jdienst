# Platform Enterprise Baseline (`apps/common`)

## Ziel

Verbindliche Baseline fuer `apps/common` als Plattformschicht: was heute bereits zentral vorhanden ist und welche Luecken fuer enterprise-faehige Nutzung noch geschlossen werden muessen.

## Bereits zentral verfuegbar

- **Audit-Grundlage:** `AuditEvent`, Integritaetskette, read-only API, Ops-Commands.
- **Request-/Trace-Kontext:** `X-Request-ID`/`X-Trace-ID` Erfassung via Middleware und Fehler-Contract.
- **Idempotency:** Key-basierte Schutzschicht fuer mutierende Endpunkte.
- **Transactional Outbox:** persistente Outbox mit Retry-Backoff und Health-Snapshot.
- **Tenant-Kontext:** Tenant-Aufloesung per Header/Fallback und Mitgliedschafts-Checks.
- **Platform Ops:** Health-, Check- und SLO-Endpunkte plus CLI-Kommandos.
- **Soft Delete / Retention:** Basismodelle und technische Cleanup-Pfade.

## Aktuelle Enterprise-Luecken (priorisiert)

1. **Schichtgrenzen:** generisches Deny-Audit-Logging liegt noch teilweise in Domain-Apps.
2. **Access Governance:** Rollenmodell ist noch grob (owner/admin/member) ohne scoped Policies.
3. **Outbox-Betriebsreife:** DLQ/Replay/feingranulare Failure-Telemetrie fehlen.
4. **Lock-Haertung:** kein Fencing-Token fuer robuste verteilte Koordination unter hoher Last.
5. **Health-Transparenz:** degradierte Teilzustandserkennung ist noch nicht durchgaengig explizit.
6. **API-Konsistenz:** Header- und Pagination-Konventionen sind noch nicht vollstaendig zentralisiert.
7. **Tenant-Isolation:** Leitplanken fuer konsistentes Query-Scoping muessen staerker erzwungen werden.

## Verbindliche Referenzpfade

- Core-Doku: `docs/backend/common/README.md`
- Gap-Analyse: `docs/backend/common/audit-gap-analysis.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
- Integrity-Hardening: `docs/backend/common/audit-integrity-hardening.md`
- Ops-Betrieb: `docs/backend/common/audit-operations.md`

## Erfolgsmessung fuer den Ausbau

- Keine `common -> domain` Runtime-Abhaengigkeit fuer generische Security-Bausteine.
- Einheitliche API-Header- und Pagination-Vertraege in allen Backend-Apps.
- Messbare Failure-Signale (statt stiller Unterdrueckung) in Platform-Health.
- Nachvollziehbare Governance fuer Tenant-Rollen und Audit-of-audit.
