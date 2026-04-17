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
- stale/missing Integritaetsverifikation (`audit_health_snapshot --require-fresh-integrity`)

## Incident- und Forensik-Ablauf

1. Incident klassifizieren (Security, Betrieb, Datenintegritaet).
2. Zeitfenster und betroffene Targets definieren.
3. Audit-Events mit technischen Logs korrelieren.
4. Ergebnis und Massnahmen revisionsfaehig dokumentieren.

## SIEM-Integration (Zielbild)

- Implementierte Commands und API-Endpunkte: `docs/backend/common/audit-interfaces.md`
- Export erfolgt als JSONL inkl. `integrity_hash`/`previous_hash`.
- Stelle sicher, dass Exporte keine sensiblen Rohdaten enthalten.
- Fuehre Integrations- und Wiederanlauftests regelmaessig durch.
- Offen: produktiver Transfer in SIEM-Pipeline inkl. Fehlerhandling/SLO.

## Verifikation

- Regelmaessige Testlaeufe fuer Export-/Archivpfade.
- Stichproben zur Datenlesbarkeit archivierter Events.
- Monitoring-Checks als Bestandteil operativer Readiness.
- Integritaetsfrische ueber `python manage.py audit_health_snapshot --require-fresh-integrity` pruefen.
- Export-Backlog-Schwellen ueber `python manage.py audit_health_snapshot --max-unexported-events <n>` absichern.

## Mindest-Evidenzkatalog (Enterprise-Restluecke)

- Nachweis monatlicher Archiv-/Export-Job-Laeufe.
- Nachweis wiederkehrender Restore-Stichproben (inkl. Ergebnisprotokoll).
- Nachweis definierter Alert-Schwellen und Reaktionszeiten.
- Nachweis Security-Review bei Aenderungen am Export-/Retention-Pfad.
- Konkretes Artefakt-Template: `docs/backend/common/audit-evidence-checklist.md`

## Querverweise

- Architektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy: `docs/backend/common/audit-security-privacy.md`
- Schnittstellen-Referenz (Commands + API): `docs/backend/common/audit-interfaces.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
- Engineering Backend: `docs/engineering/backend.md`
- Engineering Security: `docs/engineering/security.md`
- Engineering Testing: `docs/engineering/testing.md`
- Engineering API: `docs/engineering/api.md`
