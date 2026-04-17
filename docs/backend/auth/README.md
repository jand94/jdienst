# Auth

## Zweck

Das Modul `apps/auth` stellt JWT-basierte Authentifizierung bereit:

- Access-Token via `Authorization: Bearer <token>`
- Refresh-Token via HttpOnly-Cookie
- Rotating Refresh Tokens mit Blacklist-Revocation
- Audit-Events fuer Login/Refresh/Logout ueber `apps.common`

## API-Endpunkte

- `POST /api/auth/v1/login/`
  - Body: `username` (Benutzername **oder** E-Mail), `password`
  - Response: Access-Token
  - Setzt `refresh_token` Cookie
- `POST /api/auth/v1/refresh/`
  - Liest `refresh_token` Cookie
  - Response: neues Access-Token
  - Rotiert `refresh_token` Cookie
- `POST /api/auth/v1/logout/`
  - Benoetigt Bearer Access-Token
  - Blacklistet aktives Refresh-Token und loescht Cookie

## Umgebungsvariablen

- `AUTH_ACCESS_TOKEN_LIFETIME_MINUTES` (Default: `10`)
- `AUTH_REFRESH_TOKEN_LIFETIME_DAYS` (Default: `14`)
- `AUTH_JWT_ALGORITHM` (Default: `HS256`)
- `AUTH_JWT_SIGNING_KEY` (Default: `SECRET_KEY`)
- `AUTH_REFRESH_COOKIE_NAME` (Default: `refresh_token`)
- `AUTH_REFRESH_COOKIE_SECURE` (Default: `true`)
- `AUTH_REFRESH_COOKIE_HTTPONLY` (Default: `true`)
- `AUTH_REFRESH_COOKIE_SAMESITE` (Default: `Lax`)
- `AUTH_REFRESH_COOKIE_DOMAIN` (Default: leer)
- `AUTH_REFRESH_COOKIE_PATH` (Default: `/api/auth/`)
- `AUTH_REFRESH_COOKIE_MAX_AGE_SECONDS` (Default: aus Refresh-Lifetime)
- `AUTH_LOGIN_RATE` (Default: `10/minute`)
- `AUTH_REFRESH_RATE` (Default: `30/hour`)
- `AUTH_LOGOUT_RATE` (Default: `60/hour`)
- `CORS_ALLOW_CREDENTIALS` (Default: `true`, erforderlich fuer Cross-Origin-Cookie-Refresh)

## Browser/CORS-Hinweise

- Der Hybrid-Flow mit Refresh-Cookie benoetigt im Frontend `credentials: "include"` fuer Requests auf `login`, `refresh` und `logout`.
- `CORS_ALLOWED_ORIGINS` muss explizit gesetzt sein, Wildcards sind fuer Credential-Requests nicht geeignet.
- `AUTH_REFRESH_COOKIE_SECURE`:
  - Lokal mit HTTP haeufig `false`
  - Produktion mit HTTPS immer `true`

## Production Hardening

- Fuer asymmetrische Signaturen `AUTH_JWT_ALGORITHM=RS256` (oder `ES256`) setzen und getrennte Keys verwenden:
  - `AUTH_JWT_SIGNING_KEY` (privater Signierschluessel)
  - `AUTH_JWT_VERIFYING_KEY` (oeffentlicher Verifikationsschluessel)
- Optional Claim-Haertung aktivieren:
  - `AUTH_JWT_AUDIENCE`
  - `AUTH_JWT_ISSUER`
- Fuer Key-Distribution kann optional `AUTH_JWT_JWK_URL` genutzt werden.
- In reinen API-Deployments kann `AUTH_API_ENABLE_SESSION_AUTH=false` gesetzt werden, um SessionAuthentication global zu deaktivieren.

## Kompatibilitaet

Bestehende DRF-Endpunkte mit `IsAuthenticated` bleiben kompatibel. Der Login-Flow wurde mit `accounts`-Endpoints validiert (`/api/accounts/v1/users/me/`) und funktioniert mit Bearer Access-Tokens plus bestehendem Tenant-Header.
