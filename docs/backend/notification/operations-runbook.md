# Notification Operations Runbook

## Ziel

Schnelle Diagnose und Stabilisierung der Notification-Pipeline bei Queue-Lag, Delivery-Fehlern oder Digest-Stau.

## Standard-Checks (lokal)

1. Snapshot abrufen:

```bash
make notification-health
```

2. Wenn `delivery.pending_total` oder `delivery.retries_due_total` hoch sind:

```bash
make notification-dispatch
```

3. Wenn Digest-Backlog steigt (`digest.pending_total`), Build/Dispatch triggern:

```bash
make notification-digest-build
make notification-digest-dispatch
```

4. Falls keine reproduzierbaren Daten vorhanden sind, Diagnosedaten seeden:

```bash
make notification-seed-fixture TENANT_SLUG=<tenant> USER_EMAIL=<user-email>
```

5. Komplettes Recovery-Playbook als Sammelkommando:

```bash
make notification-pipeline-recover
```

## Interpretation

- `delivery.pending_total`: Gesamtzahl noch nicht final verarbeiteter Zustellungen.
- `delivery.terminal_failed_total`: Endgueltig fehlgeschlagene Zustellungen (keine weiteren Retries).
- `delivery.retryable_failed_total`: Fehlschlaege, die noch erneut versucht werden.
- `delivery.oldest_pending_age_seconds`: Alter der aeltesten wartenden Zustellung.
- `digest.pending_total`: Nicht versendete Digests.

## Eskalationspfad

1. **Transient Mail-Fehler** (`smtp_connect_error`, `smtp_server_disconnected`):
   - Relay/Konnektivitaet pruefen
   - danach `make notification-dispatch` erneut ausfuehren
2. **Permanent Mail-Fehler** (`recipient_missing_email`, `smtp_recipients_refused`):
   - Benutzerdaten/Empfaengeradresse korrigieren
   - betroffene Notification ggf. erneut erzeugen
3. **Ops-Snapshot kritisch (`passed=false`)**:
   - Werte gegen `NOTIFICATION_HEALTH_*` Schwellwerte abgleichen
   - bei dauerhaftem Backlog Worker/Beat-Last und Redis-Verfuegbarkeit pruefen

## Incident-Drills

### Drill A: Delivery-Stau simulieren und aufloesen

1. `make notification-seed-fixture ...`
2. `make notification-health` (Stau bestaetigen)
3. `make notification-dispatch`
4. `make notification-health` (Rueckgang bestaetigen)

### Drill B: Digest-Backlog simulieren und aufloesen

1. `make notification-seed-fixture ...`
2. `make notification-digest-build`
3. `make notification-digest-dispatch`
4. `make notification-health` (Digest pending sollte sinken)

## Wichtige Endpunkte

- API Snapshot: `GET /api/notification/v1/ops/health-snapshot/`
- Delivery Queue Trigger (Task): `notification.dispatch_pending_deliveries`
- Digest Build Trigger (Task): `notification.build_pending_digests`
- Digest Dispatch Trigger (Task): `notification.dispatch_pending_digests`

## Nachbereitung

- Relevante `security.permission.denied` und Notification-Audit-Events pruefen.
- Incident-Timeline mit `request_id`/`trace_id` aus Logs dokumentieren.
