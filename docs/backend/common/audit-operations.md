# Audit Operations (`apps/common`)

## Zweck

Dieses Dokument beschreibt den operativen Betrieb der Auditierung:
Retention, Archivierung, Monitoring und Incident-/Forensik-Ablauf.

## Betriebsziele

- Auditdaten sind verfuegbar und auswertbar.
- kritische Ereignisse sind zeitnah auffindbar.
- Integritaets- und Vollstaendigkeitsrisiken werden frueh erkannt.

## Retention-Strategie (aktueller Stand + Zielbild)

- Aktuell: technische Archivierungsmarkierung via `archived_at`.
- Ziel: Event-Klassen mit verbindlichen Aufbewahrungsfristen
  (z. B. security-kritisch, operativ, technisch).
- Ziel: Trennung aktiver Datenhaltung und revisionsfester Archivablage.
- Vor Loeschung: fachliche und regulatorische Freigabe dokumentieren.

Hinweis: Konkrete Fristen sind organisationsabhaengig und muessen ausserhalb dieses Dokuments
final freigegeben werden.

## Archivierung

- Implementiert: `python manage.py audit_archive_events --before-days <n>`.
- Implementiert: `python manage.py audit_archive_events --use-retention-policy`.
- Aktuell wird per Zeitgrenze `archived_at` gesetzt (logische Archivierung).
- Offen: physische Auslagerung in kostenguensigen/revisionsfesten Storage.
- Restore-Prozess fuer Stichproben und Incident-Untersuchungen dokumentieren.

## Monitoring und Alerting

Empfohlene Kennzahlen:

- Audit-Write-Fehlerrate
- Event-Volumen pro Quelle (`metadata.source`)
- Latenz zwischen Ereignis und Persistierung
- Anteil nicht exportierter Events (`exported_at IS NULL`)
- ungewoehnliche Muster (z. B. viele `admin.delete` in kurzer Zeit)

Empfohlene Alerts:

- Ausfall der Audit-Schreibpfade
- dauerhaft hohe Fehlerrate
- signifikante Event-Abweichungen gegen Baseline

## Incident- und Forensik-Ablauf

1. Incident klassifizieren (Security, Betrieb, Datenintegritaet).
2. Zeitfenster und betroffene Targets definieren.
3. Audit-Events mit technischen Logs korrelieren.
4. Ergebnis und Massnahmen revisionsfaehig dokumentieren.

## SIEM-Integration (Zielbild)

- Implementiert: `python manage.py audit_export_siem --limit <n> [--mark-exported]`
  mit JSONL-Ausgabe und Feldern inkl. `integrity_hash`/`previous_hash`.
- Implementiert: `python manage.py audit_backfill_integrity_hashes [--dry-run]` fuer Legacy-Reparatur fehlender Hashes.
- Implementiert: `python manage.py audit_health_snapshot --window-hours <n>` fuer Monitoring-Daten.
- Implementiert: `python manage.py audit_verify_integrity [--create-checkpoint]` fuer periodische Verifikation.
- API-Expose fuer Operatoren:
  - `GET /api/common/v1/audit-ops/health-snapshot/`
  - `POST /api/common/v1/audit-ops/verify-integrity/`
  - `GET /api/common/v1/audit-ops/siem-export-preview/`
  - `POST /api/common/v1/audit-ops/archive-events/`
  - `POST /api/common/v1/audit-ops/setup-roles/`
- Stelle sicher, dass Exporte keine sensiblen Rohdaten enthalten.
- Fuehre Integrations- und Wiederanlauftests regelmaessig durch.
- Offen: produktiver Transfer in SIEM-Pipeline inkl. Fehlerhandling/SLO.

## Verifikation

- Regelmaessige Testlaeufe fuer Export-/Archivpfade.
- Stichproben zur Datenlesbarkeit archivierter Events.
- Monitoring-Checks als Bestandteil operativer Readiness.

## Mindest-Evidenzkatalog (Enterprise-Restluecke)

- Nachweis monatlicher Archiv-/Export-Job-Laeufe.
- Nachweis wiederkehrender Restore-Stichproben (inkl. Ergebnisprotokoll).
- Nachweis definierter Alert-Schwellen und Reaktionszeiten.
- Nachweis Security-Review bei Aenderungen am Export-/Retention-Pfad.
- Konkretes Artefakt-Template: `docs/backend/common/audit-evidence-checklist.md`

## Querverweise

- Architektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy: `docs/backend/common/audit-security-privacy.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
- Engineering Backend: `docs/engineering/backend.md`
- Engineering Security: `docs/engineering/security.md`
- Engineering Testing: `docs/engineering/testing.md`
- Engineering API: `docs/engineering/api.md`
