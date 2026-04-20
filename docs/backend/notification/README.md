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

## API-Ueberblick (v1)

Inbox:

- `GET /api/notification/v1/notifications/` (paginiert)
- `GET /api/notification/v1/notifications/unread-count/`
- `POST /api/notification/v1/notifications/{id}/mark-read/`
- `POST /api/notification/v1/notifications/bulk-mark-read/`
- `POST /api/notification/v1/notifications/{id}/archive/`
- `POST /api/notification/v1/notifications/bulk-archive/`

Praeferenzen:

- `GET /api/notification/v1/preferences/` (paginiert)
- `PATCH /api/notification/v1/preferences/{id}/`

Ops:

- `GET /api/notification/v1/ops/health-snapshot/`

Realtime:

- `ws://<host>/ws/notification/v1/inbox/?token=<jwt>`

## Lokale Diagnose

- `make notification-health` fuer Pipeline-Snapshot
- `make notification-dispatch` fuer sofortiges Abarbeiten faelliger Deliveries
- `make notification-digest-build` und `make notification-digest-dispatch` fuer Digest-Rueckstau
- `make notification-pipeline-recover` fuer kombinierten Recovery-Lauf
- `make notification-seed-fixture TENANT_SLUG=<slug> USER_EMAIL=<mail>` fuer Diagnosedaten

## Runbook

- Operational Playbook: `docs/backend/notification/operations-runbook.md`

## Querverweise

- Engineering-Regelwerk: `docs/engineering/notifications.md`
- API-Vertrag/OpenAPI: `docs/engineering/api.md`
