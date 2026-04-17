# Audit Evidence Checklist (`apps/common`)

## Ziel

Dieses Dokument definiert die minimalen Betriebsnachweise fuer Enterprise-Audit im Sinne
von `docs/engineering/security.md`, `docs/engineering/backend.md` und `docs/engineering/testing.md`.

## Pflichtnachweise pro Monat

- Erfolgreicher Lauf von `audit_archive_events` (mit Parametern und Zeitstempel).
- Erfolgreicher Lauf von `audit_export_siem` inkl. Export-/Fehler-Summary.
- Integritaetsnachweis via `audit_verify_integrity` inkl. Status und gepruefter Event-Anzahl.
- Nachweis, dass Audit-Reader-Rollen mit `audit_setup_roles` konsistent sind.

## Pflichtnachweise pro Quartal

- Restore-Stichprobe archivierter Audit-Events (Ablauf, Ergebnis, Abweichungen).
- Review der Alert-Schwellen fuer Audit-Write-Fehler, Export-Backlog und Anomalien.
- Security-Review fuer geaenderte Audit- oder SIEM-Exportpfade.

## Artefakt-Format (Mindeststandard)

- Timestamp (UTC)
- Umgebung (dev/stage/prod)
- Ausgefuehrter Befehl mit Parametern
- Ergebnisstatus (`passed` / `failed`)
- Verantwortlicher (User/Team)
- Link oder Referenz auf Ticket/Incident (falls vorhanden)
