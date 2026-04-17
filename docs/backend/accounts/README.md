# accounts

## Zweck

`accounts` kapselt User-bezogene Funktionen inklusive API-Endpunkte fuer
Profilzugriff/-pflege und Security-Auditing in Kombination mit `apps/common`.

## Struktur

- `models/user.py`: projektweites User-Modell (`accounts.User`)
- `admin/user.py`: Admin-Registrierung mit Audit-Mixin
- `api/v1/services/account_user_service.py`: Profil-Update/Deaktivierung + Audit-Events
- `api/v1/services/account_security_service.py`: Auth-/Permission-Audit-Helfer
- `api/v1/serializers/user.py`: Read/Update-Serializer
- `api/v1/permissions/user.py`: Objektberechtigung (self oder staff)
- `api/v1/views/user.py`: User-ViewSet inkl. `me` und `me/deactivate`
- `api/v1/schema/user.py`: drf-spectacular Schema-Definitionen
- `tests/`: Unit-/Integrations-Tests fuer Services und API

## API-Endpunkte (v1)

- `GET /api/accounts/v1/users/` (nur staff)
- `GET /api/accounts/v1/users/me/`
- `PATCH /api/accounts/v1/users/me/`
- `POST /api/accounts/v1/users/me/deactivate/`
- `GET /api/accounts/v1/users/{id}/`
- `PATCH /api/accounts/v1/users/{id}/` (nur self oder staff)

## Audit-Verhalten

- Profilaenderungen erzeugen `accounts.user.updated`.
- Deaktivierung erzeugt `accounts.user.deactivated`.
- Permission-Verletzungen erzeugen `security.permission.denied`.
- Auth-Versuche koennen via `log_auth_attempt(...)` protokolliert werden.
