# Backend (Django & DRF)

Dieses Verzeichnis enthält das Backend des Projekts, basierend auf:

- Django
- Django REST Framework (DRF)
- PostgreSQL
- Redis / Celery (für asynchrone Tasks)

Die Architektur folgt den Regeln aus `CLAUDE.md` und `docs/engineering/backend.md`.

---

## Grundprinzip

Das Backend wird **primär über Docker Compose betrieben**.  
Direkte lokale Python-Ausführung ist möglich, aber **nicht der Standard**.

---

## Schnellstart (empfohlen)

### 1. Gesamten Stack starten

Im Repository-Root:

```bash
docker compose up --build

Oder (wenn Makefile vorhanden):

make up
2. Migrationen ausführen
docker compose exec backend python manage.py migrate

oder:

make migrate
3. Superuser erstellen (optional)
docker compose exec backend python manage.py createsuperuser
4. Backend erreichen
API: http://localhost:8000
Admin: http://localhost:8000/admin
Lokale Entwicklung ohne Docker (optional)

Nur verwenden, wenn bewusst ohne Container gearbeitet wird:

cd backend

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver

⚠️ Dieser Workflow ist nicht kanonisch und kann von der Container-Umgebung abweichen.

Projektstruktur (verbindlich)

Jede Django-App folgt der domänenorientierten Struktur:

app_name/
├── admin/
├── models/
├── api/
│   └── v1/
│       ├── services/
│       ├── views/
│       ├── serializers/
│       ├── permissions/
│       └── schema/
Wichtige Regeln
Keine generischen Dateinamen (models.py, views.py, etc.)
Keine Logik in __init__.py
Business-Logik gehört in Services
Views bleiben dünn

Details: docs/engineering/backend.md

API & OpenAPI
API-Dokumentation wird mit drf-spectacular erzeugt
OpenAPI-Schema ist Teil des Vertrags

Schema generieren:

docker compose exec backend python manage.py spectacular --file schema.yaml

Validieren:

docker compose exec backend python manage.py spectacular --validate --fail-on-warn

Details: docs/engineering/api.md

Tests

Backend-Tests ausführen:

docker compose exec backend pytest

oder:

make test-be
Test-Grundsätze
Business-Logik muss getestet werden
API-Verträge müssen getestet werden
Security-relevante Pfade müssen getestet werden

Details: docs/engineering/testing.md

Linting & Qualität
make lint

oder manuell:

ruff check .
Hintergrundjobs (Celery)

Wenn aktiviert:

docker compose up worker

oder:

make worker
Umgebungsvariablen

Konfiguration erfolgt über .env.

Beispiel:

DEBUG=1
DATABASE_URL=postgres://user:password@db:5432/app
REDIS_URL=redis://redis:6379/0
Wichtige Engineering-Regeln
Keine Business-Logik in Views oder Serializern
Keine direkten LLM-Aufrufe außerhalb von Services
API-Schema immer aktuell halten
Änderungen müssen durch Tests abgesichert sein
Security-by-default anwenden
Relevante Dokumentation
Architektur & Backend: docs/engineering/backend.md
API & OpenAPI: docs/engineering/api.md
Tests: docs/engineering/testing.md
Security: docs/engineering/security.md
Docker: docs/engineering/docker.md
CI: docs/engineering/ci.md
Ziel

Dieses Backend ist ausgelegt für:

Skalierbarkeit
Wartbarkeit
Sicherheit
Auditierbarkeit
Produktionsnähe

Der Code soll den Standards eines erfahrenen Enterprise-Engineering-Teams entsprechen.