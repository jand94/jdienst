# Audit Integrity Hardening (`apps/common`)

## Ziel

Integritätsnachweise so operationalisieren, dass periodische Verifikation,
externe Signatur-Härtung und revisionsfeste Ablage klar geplant und prüfbar sind.

## Aktueller technischer Stand

- Hash-Kette je Event (`previous_hash`/`integrity_hash`)
- Append-only Enforcement auf `AuditEvent`
- Integritätsverifikation via:
  - `python manage.py audit_verify_integrity`
  - `POST /api/common/v1/audit-ops/verify-integrity/`
- Checkpoints mit HMAC-Signatur (`AUDIT_INTEGRITY_SIGNING_KEY`)

## Operative Mindestanforderung (ab sofort)

- Verifikation mindestens taeglich ausführen.
- `audit_health_snapshot --require-fresh-integrity` als Guard in Automationen nutzen.
- Fehlende oder veraltete Verifikation als Incident behandeln.

## Externe Hardening-Strategie (Roadmap)

### Stufe 1: Externer Signaturnachweis

- Signaturen nicht nur mit internem App-Secret, sondern ueber separaten KMS-Key.
- Key-Rotation mit dokumentierter Historie.
- Signatur-Validierung in periodischen Kontrolljobs.

### Stufe 2: Revisionsfeste Ablage (WORM)

- Exportierte Audit-Artefakte in Object Storage mit Retention Lock / WORM-Modus.
- Manipulationsschutz auf Storage-Ebene als zweite Verteidigungslinie.
- Restore-Drills aus WORM-Ablage quartalsweise.

### Stufe 3: Compliance-Evidenz

- Nachweisbare Kette: Event -> Checkpoint -> externe Signatur -> immutable Storage.
- Verknüpfung mit `audit-evidence-checklist.md` fuer monatliche/quartalsweise Nachweise.

## Abnahmekriterien

- Periodische Verifikation technisch erzwungen und monitorbar.
- Dokumentierte Architektur fuer KMS-Signatur und WORM-Retention.
- Wiederherstellbarkeit und Nachweisbarkeit ueber Evidence-Artefakte gegeben.
