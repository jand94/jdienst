# Backend (Django & DRF)

Dieses Verzeichnis enthaelt das Backend des Projekts mit:

- Django + Django REST Framework
- PostgreSQL
- Redis + Celery + Channels

Die Architektur folgt `CLAUDE.md` und den Regeln unter `docs/engineering/`.

## Betrieb (kanonisch)

Das Backend wird primaer ueber Docker Compose betrieben.

Im Repository-Root:

```bash
make up-d
make migrate
```

Optional:

```bash
make create-superuser
```

Erreichbarkeit:

- API: `http://localhost:8000`
- Admin: `http://localhost:8000/admin`

## Wichtige Befehle

- `make be-shell` - Shell im Backend-Container
- `make test-be` - Backend-Tests
- `make schema-validate` - OpenAPI validieren (`--fail-on-warn`)
- `make worker` / `make beat` - Celery Worker/Beat starten

Notification-spezifisch:

- `make notification-health`
- `make notification-dispatch`
- `make notification-digest-build`
- `make notification-digest-dispatch`
- `make notification-pipeline-recover`
- `make notification-seed-fixture TENANT_SLUG=<slug> USER_EMAIL=<mail>`

## Architekturregeln (Kurzfassung)

- Business-Logik in `api/v1/services/`
- Views duenn halten
- Keine Fachlogik in `__init__.py`
- OpenAPI-Schema ist Vertragsbestandteil
- Mutierende/security-kritische Flows mit Audit-Events absichern

Details:

- `docs/engineering/backend.md`
- `docs/engineering/api.md`
- `docs/engineering/testing.md`
- `docs/engineering/security.md`
- `docs/backend/common/README.md`

## Notification-Dokumentation

- `docs/backend/notification/README.md`
- `docs/backend/notification/operations-runbook.md`