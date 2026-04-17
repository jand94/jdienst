# Audit Operations (`apps/common`)

## Zweck

Dieses Dokument beschreibt den operativen Betrieb der Auditierung:
Retention, Archivierung, Monitoring und Incident-/Forensik-Ablauf.

## Betriebsziele

- Auditdaten sind verfuegbar und auswertbar.
- kritische Ereignisse sind zeitnah auffindbar.
- Integritaets- und Vollstaendigkeitsrisiken werden frueh erkannt.

## Retention-Strategie (Zielbild)

- Definiere Event-Klassen mit Aufbewahrungsfristen (z. B. Security-kritisch, operativ, technisch).
- Trenne aktive Datenhaltung von Archivdaten.
- Vor Loeschung: fachliche und regulatorische Freigabe dokumentieren.

Hinweis: Konkrete Fristen sind organisationsabhaengig und muessen ausserhalb dieses Dokuments
final freigegeben werden.

## Archivierung

- Regelbasierter Export alter Auditdaten in kostenguensigeren Storage.
- Sicherstellen, dass archivierte Daten weiterhin nachweisbar und lesbar sind.
- Restore-Prozess fuer Stichproben und Incident-Untersuchungen dokumentieren.

## Monitoring und Alerting

Empfohlene Kennzahlen:

- Audit-Write-Fehlerrate
- Event-Volumen pro Quelle (`metadata.source`)
- Latenz zwischen Ereignis und Persistierung
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

- Definiere standardisiertes Exportformat und Mindestfelder.
- Stelle sicher, dass Exporte keine sensiblen Rohdaten enthalten.
- Fuehre Integrations- und Wiederanlauftests regelmaessig durch.

## Verifikation

- Regelmaessige Testlaeufe fuer Export-/Archivpfade.
- Stichproben zur Datenlesbarkeit archivierter Events.
- Monitoring-Checks als Bestandteil operativer Readiness.

## Querverweise

- Architektur: `docs/backend/common/audit-architecture.md`
- Security/Privacy: `docs/backend/common/audit-security-privacy.md`
- Roadmap: `docs/backend/common/audit-roadmap.md`
- Engineering Backend: `docs/engineering/backend.md`
- Engineering Security: `docs/engineering/security.md`
