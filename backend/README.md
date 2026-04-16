# Backend

Dieses Verzeichnis enthaelt das Django-Backend fuer das Projekt.

## Voraussetzungen

- Python 3.11+ (empfohlen)
- `pip`
- Optional: virtuelle Umgebung (`venv`)

## Lokales Setup

1. In das Backend-Verzeichnis wechseln:
   - `cd backend`
2. Virtuelle Umgebung erstellen und aktivieren (optional, empfohlen):
   - Windows (PowerShell): `python -m venv .venv` und `.\.venv\Scripts\Activate.ps1`
   - macOS/Linux: `python -m venv .venv` und `source .venv/bin/activate`
3. Abhaengigkeiten installieren:
   - `pip install -r requirements.txt`
4. Datenbank-Migrationen ausfuehren:
   - `python manage.py migrate`
5. Development-Server starten:
   - `python manage.py runserver`

Standard-URL lokal: [http://localhost:8000](http://localhost:8000)

## Tests

- Alle Tests ausfuehren: `python manage.py test`

## Nuetzliche Django-Befehle

- Neue Migrationen erstellen: `python manage.py makemigrations`
- Migrationen anwenden: `python manage.py migrate`
- Admin-User anlegen: `python manage.py createsuperuser`

## Hinweise

- Konfiguration und URL-Routing liegen unter `backend/` (Django-Projektpaket).
- Einstiegspunkt fuer Management-Befehle ist `manage.py`.
