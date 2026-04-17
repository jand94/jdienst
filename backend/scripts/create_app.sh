#!/bin/bash

set -euo pipefail

if [ -z "${BASH_VERSION:-}" ]; then
    echo "Dieses Script muss mit bash ausgefuehrt werden."
    echo "Beispiel: bash backend/scripts/create_app.sh <app_name>"
    exit 1
fi

if [ -z "${1:-}" ]; then
    echo "Bitte App-Namen angeben!"
    echo "Verwendung: ./create_app.sh app_name"
    exit 1
fi

APP_NAME="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
REPO_ROOT="$(cd "$BACKEND_ROOT/.." && pwd)"
BASE_SETTINGS_FILE="$BACKEND_ROOT/backend/base.py"
ROOT_URLS_FILE="$BACKEND_ROOT/backend/urls.py"

if ! [[ "$APP_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Ungueltiger App-Name: '$APP_NAME'"
    echo "Erlaubt: lowercase, digits, underscore; muss mit Buchstaben beginnen."
    exit 1
fi

if [ ! -f "$BACKEND_ROOT/manage.py" ]; then
    echo "Ungueltige Backend-Struktur: manage.py nicht gefunden."
    exit 1
fi

if [ ! -f "$BASE_SETTINGS_FILE" ]; then
    echo "Einstellungsdatei nicht gefunden: $BASE_SETTINGS_FILE"
    exit 1
fi

if [ ! -f "$ROOT_URLS_FILE" ]; then
    echo "Root-URL-Datei nicht gefunden: $ROOT_URLS_FILE"
    exit 1
fi

APP_PATH="$BACKEND_ROOT/apps/$APP_NAME"
DOCS_APP_PATH="$REPO_ROOT/docs/backend/$APP_NAME"

if [ -d "$APP_PATH" ]; then
    echo "App '$APP_NAME' existiert bereits unter $APP_PATH"
    exit 1
fi

echo "Erstelle minimale Django-App-Struktur fuer: $APP_NAME"

# Domain-orientierte Ordnerstruktur gemaess Projektregeln.
mkdir -p "$APP_PATH/admin"
mkdir -p "$APP_PATH/models"
mkdir -p "$APP_PATH/exceptions"
mkdir -p "$APP_PATH/migrations"
mkdir -p "$APP_PATH/api/v1/services"
mkdir -p "$APP_PATH/api/v1/views"
mkdir -p "$APP_PATH/api/v1/serializers"
mkdir -p "$APP_PATH/api/v1/permissions"
mkdir -p "$APP_PATH/api/v1/schema"
mkdir -p "$APP_PATH/tests/factories"
mkdir -p "$APP_PATH/tests/integration/api"
mkdir -p "$APP_PATH/tests/integration/services"
mkdir -p "$APP_PATH/tests/unit/models"
mkdir -p "$APP_PATH/tests/unit/services"
mkdir -p "$DOCS_APP_PATH"

# Nur leere Package-Dateien (keine Inhalte/Boilerplate).
touch "$APP_PATH/__init__.py"
touch "$APP_PATH/admin/__init__.py"
touch "$APP_PATH/models/__init__.py"
touch "$APP_PATH/exceptions/__init__.py"
touch "$APP_PATH/migrations/__init__.py"
touch "$APP_PATH/api/__init__.py"
touch "$APP_PATH/api/v1/__init__.py"
touch "$APP_PATH/api/v1/services/__init__.py"
touch "$APP_PATH/api/v1/views/__init__.py"
touch "$APP_PATH/api/v1/serializers/__init__.py"
touch "$APP_PATH/api/v1/permissions/__init__.py"
touch "$APP_PATH/api/v1/schema/__init__.py"
touch "$APP_PATH/tests/__init__.py"
touch "$APP_PATH/tests/factories/__init__.py"
touch "$APP_PATH/tests/integration/__init__.py"
touch "$APP_PATH/tests/integration/api/__init__.py"
touch "$APP_PATH/tests/integration/services/__init__.py"
touch "$APP_PATH/tests/unit/__init__.py"
touch "$APP_PATH/tests/unit/models/__init__.py"
touch "$APP_PATH/tests/unit/services/__init__.py"

APP_CLASS_NAME="$(echo "$APP_NAME" | sed -E 's/(^|_)([a-z])/\U\2/g')Config"

cat > "$APP_PATH/apps.py" << EOL
from django.apps import AppConfig


class $APP_CLASS_NAME(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.$APP_NAME"
EOL

cat > "$APP_PATH/urls.py" << EOL
from django.urls import include, path

urlpatterns = [
    path("v1/", include("apps.$APP_NAME.api.v1.urls")),
]
EOL

cat > "$APP_PATH/api/v1/urls.py" << EOL
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    *router.urls,
]
EOL

cat > "$APP_PATH/tests/conftest.py" << EOL
import pytest
from rest_framework.test import APIClient
from apps.common.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory()
EOL

cat > "$DOCS_APP_PATH/README.md" << EOL
# $APP_NAME

## Zweck

Kurze Beschreibung des Domaenenmoduls \`$APP_NAME\`.

## Struktur

- \`models/\`: Domaenenmodelle
- \`exceptions/\`: domaenenspezifische Fehler
- \`api/v1/\`: API-Transport (Views, Serializer, Permissions, Services, Schema)
- \`admin/\`: Admin-Registrierungen
- \`tests/\`: Modul-Tests

## Naechste Schritte

1. Fachliche Dateien in den jeweiligen Ordnern anlegen
2. Exporte in \`__init__.py\` pflegen
3. API-Endpunkte in \`api/v1\` umsetzen
4. Tests ergaenzen
EOL

python3 - << PY
from pathlib import Path

app_name = "$APP_NAME"
base_settings_file = Path("$BASE_SETTINGS_FILE")
root_urls_file = Path("$ROOT_URLS_FILE")
app_entry = f'    "apps.{app_name}",'
settings_content = base_settings_file.read_text()

if app_entry in settings_content:
    print(f"INTERNAL_APPS bereits registriert: apps.{app_name}")
else:
    marker = "INTERNAL_APPS: list[str] = ["
    marker_idx = settings_content.find(marker)
    if marker_idx == -1:
        raise SystemExit("Konnte INTERNAL_APPS-Definition in base.py nicht finden.")

    list_start = marker_idx + len(marker)
    list_end_relative = settings_content[list_start:].find("]")
    if list_end_relative == -1:
        raise SystemExit("Konnte Abschluss von INTERNAL_APPS-Liste nicht finden.")

    insert_at = list_start + list_end_relative
    settings_content = settings_content[:insert_at] + f"\\n{app_entry}" + settings_content[insert_at:]
    base_settings_file.write_text(settings_content)
    print(f"INTERNAL_APPS aktualisiert: apps.{app_name}")

route_entry = f'    path("api/{app_name}/", include("apps.{app_name}.urls")),'
urls_content = root_urls_file.read_text()

if "from django.urls import path" in urls_content and "from django.urls import include, path" not in urls_content:
    urls_content = urls_content.replace("from django.urls import path", "from django.urls import include, path")
elif "from django.urls import include, path" not in urls_content and "from django.urls import include" not in urls_content:
    raise SystemExit("Konnte django.urls-Import in backend/urls.py nicht automatisch anpassen.")

if route_entry in urls_content:
    print(f"Root-URL bereits registriert: api/{app_name}/")
else:
    marker = "urlpatterns = ["
    marker_idx = urls_content.find(marker)
    if marker_idx == -1:
        raise SystemExit("Konnte urlpatterns in backend/urls.py nicht finden.")

    list_start = marker_idx + len(marker)
    list_end_relative = urls_content[list_start:].find("]")
    if list_end_relative == -1:
        raise SystemExit("Konnte Abschluss von urlpatterns nicht finden.")

    insert_at = list_start + list_end_relative
    urls_content = urls_content[:insert_at] + f"\\n{route_entry}" + urls_content[insert_at:]
    root_urls_file.write_text(urls_content)
    print(f"Root-URL registriert: api/{app_name}/")
PY

echo "Fertig: $APP_PATH"
echo "Dokumentationsordner angelegt: $DOCS_APP_PATH"
echo ""
echo "Naechste Schritte (manuell):"
echo "1) Fachliche Dateien (z. B. kunde.py) in den Ordnern anlegen"
echo "2) Migrationen erstellen (python manage.py makemigrations)"
echo "3) Tests erweitern"
