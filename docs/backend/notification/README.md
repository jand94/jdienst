# notification

## Zweck

Zentrales Benachrichtigungsmodul fuer Inbox, Mail, Realtime und Digest mit Auditierbarkeit und operativer Beobachtbarkeit.

## Struktur

- `models/`: Domaenenmodelle (`Notification`, `NotificationDelivery`, `NotificationDigest`, ...)
- `api/v1/`: API-Transport (Views, Serializer, Permissions, Services, Schema)
- `tasks/`: Celery-Tasks fuer Delivery-/Digest-Verarbeitung
- `realtime/`: Channels/WebSocket-Integration
- `management/commands/`: Diagnose- und Seed-Kommandos
- `tests/`: Unit-/Integrations- und Contract-Tests

## Lokale Diagnose

- `make notification-health` fuer Pipeline-Snapshot
- `make notification-dispatch` fuer sofortiges Abarbeiten faelliger Deliveries
- `make notification-seed-fixture TENANT_SLUG=<slug> USER_EMAIL=<mail>` fuer Diagnosedaten

## Runbook

- Operational Playbook: `docs/backend/notification/operations-runbook.md`
