# Audit Coverage Inventory (`apps/common`)

## Zweck

Dieses Dokument listet die aktuell als kritisch eingestuften Write- und Security-Flows
inklusive Audit-Abdeckung und Testnachweisen.

## Kritische Flows und Abdeckung

| Domäne | Flow | Audit-Event | Implementierung | Testabdeckung |
|---|---|---|---|---|
| Accounts | Profilupdate (`PATCH /users/me`, `PATCH /users/{id}`) | `accounts.user.updated` | `apps/accounts/api/v1/services/account_user_service.py` | `apps/accounts/tests/unit/services/test_account_user_service.py`, `apps/accounts/tests/integration/api/test_account_user_api.py` |
| Accounts | Self-Deactivation (`POST /users/me/deactivate`) | `accounts.user.deactivated` | `apps/accounts/api/v1/services/account_user_service.py` | `apps/accounts/tests/unit/services/test_account_user_service.py`, `apps/accounts/tests/integration/api/test_account_user_api.py` |
| Accounts | Permission Denied | `security.permission.denied` | `apps/accounts/api/v1/services/account_security_service.py` | `apps/accounts/tests/unit/services/test_account_security_service.py`, `apps/accounts/tests/integration/api/test_account_user_api.py` |
| Accounts | Login Attempt | `auth.login.succeeded` / `auth.login.failed` | `apps/accounts/api/v1/services/account_security_service.py` | `apps/accounts/tests/unit/services/test_account_security_service.py` |
| Common | Integrity Verification | `common.audit_integrity.verified` | `apps/common/api/v1/services/audit_integrity_service.py` | `apps/common/tests/unit/services/test_audit_integrity_service.py`, `apps/common/tests/integration/api/test_audit_ops_api.py` |
| Common | Audit Read Access | `common.audit_event.read` | `apps/common/api/v1/services/audit_reader_service.py` | `apps/common/tests/integration/api/test_audit_event_api.py` |

## Metadaten-Kontrakt

Alle Events aus den oben gelisteten Flows enthalten mindestens:

- `metadata.source`
- `metadata.request_id` (oder `null`)
- `metadata.trace_id` (oder `null`)

Der Kontrakt wird zentral in `apps/common/api/v1/services/audit_service.py` normalisiert.

## CI-Absicherung

Die Coverage wird blockierend über folgende Test-Suiten abgesichert:

- `apps/common/tests/unit/services/test_audit_service.py`
- `apps/common/tests/integration/api/test_audit_event_api.py`
- `apps/common/tests/integration/api/test_audit_ops_api.py`
- `apps/accounts/tests/unit/services/test_account_user_service.py`
- `apps/accounts/tests/unit/services/test_account_security_service.py`
- `apps/accounts/tests/integration/api/test_account_user_api.py`

## Offene Erweiterungen

- Weitere Domain-Apps bei Einführung analog inventarisieren.
- Neue kritische Write-Flows nur mit Audit-Event + Testnachweis in diese Matrix aufnehmen.
