# Authorization Permission Matrix

## Zweck

Dieses Dokument beschreibt die aktuelle AuthZ-Logik fuer Frontend und Backend als gemeinsame Referenz fuer Engineering, QA und Review.

Die Quelle fuer effektive Capabilities ist `GET /api/accounts/v1/users/me/`.

## Capability-Response (`/users/me`)

Der Endpoint liefert tenant-spezifisch:

- `permissions: string[]`
- `feature_flags: string[]`
- `current_tenant_role: "owner" | "admin" | "member" | null`

Die Berechnung erfolgt zentral in:

- `backend/apps/accounts/api/v1/services/account_user_access_service.py`

## Basis-Permissions (alle aktiven Tenant-Mitglieder)

- `dashboard.view`
- `reports.view`
- `settings.view`
- `accounts.self.read`
- `accounts.self.update`
- `accounts.tenants.read`

## Tenant-Rollen -> zusaetzliche Permissions

- `member`
  - keine zusaetzlichen Permissions
- `admin`
  - `tenant.members.manage`
- `owner`
  - `tenant.members.manage`
  - `tenant.settings.manage`

## Staff-Erweiterung

Wenn `user.is_staff == true`, kommen additiv hinzu:

- `tenant.members.manage`
- `tenant.settings.manage`

## Audit-bezogene Permissions

Diese werden aus vorhandenen Backend-Checks abgeleitet:

- `audit.events.read`
  - gesetzt, wenn `is_audit_reader(user)` wahr ist
- `audit.ops.manage`
  - gesetzt, wenn `is_audit_operator(user)` wahr ist

Die zugrunde liegenden Permission-Pruefungen liegen in:

- `backend/apps/common/api/v1/services/audit_reader_service.py`
- `backend/apps/common/api/v1/permissions/audit_reader.py`
- `backend/apps/common/api/v1/permissions/audit_operator.py`

## Feature Flags

Aktuell:

- `dynamic_authz_navigation`
  - immer gesetzt (aktivierter globaler AuthZ-Flow)
- `audit_ops_enabled`
  - gesetzt, wenn `audit.ops.manage` vorhanden ist

## Frontend-Mapping (Permission -> Sichtbarkeit)

Navigation wird zentral gefiltert in:

- `frontend/lib/navigation/navigation-policy.ts`

Aktuelle Seiten-Gates:

- `/` benoetigt `dashboard.view`
- `/reports` benoetigt `reports.view`
- `/settings` benoetigt `settings.view`
- `/audit` benoetigt eines von:
  - `audit.events.read`
  - `audit.ops.manage`
- `/audit/ops` benoetigt `audit.ops.manage`

Route-/Component-Guards nutzen:

- `frontend/components/auth/RequireAccess.tsx`
- `frontend/components/auth/AuthProvider.tsx` (`can`, `canAny`, `hasFeature`)

## QA-Checkliste (Smoke)

- `member` sieht Dashboard, Reports, Settings; kein Audit Ops.
- `admin` sieht zusaetzlich Member-Management-bezogene Bereiche (falls UI vorhanden).
- `owner` hat zusaetzlich Tenant-Settings-Management.
- Audit-Reader sieht Audit-Events.
- Audit-Operator sieht Audit-Events und Audit-Ops.
- Tenant-Wechsel fuehrt zu neuem Permission-Set in `/users/me`.

## Beispiel-Userprofile (QA-Referenz)

### Profil: `member` (kein staff, kein Audit-Grant)

- **Erwartete Kern-Permissions**
  - `dashboard.view`
  - `reports.view`
  - `settings.view`
  - `accounts.self.read`
  - `accounts.self.update`
  - `accounts.tenants.read`
- **Nicht erwartet**
  - `tenant.members.manage`
  - `tenant.settings.manage`
  - `audit.events.read`
  - `audit.ops.manage`
- **Erwartete Navigation**
  - sichtbar: `/`, `/reports`, `/settings`
  - nicht sichtbar: `/audit`, `/audit/ops`

### Profil: `owner` (kein staff, kein Audit-Grant)

- **Erwartete Zusatz-Permissions**
  - `tenant.members.manage`
  - `tenant.settings.manage`
- **Erwartete Navigation**
  - sichtbar: `/`, `/reports`, `/settings`
  - nicht sichtbar (ohne Audit-Rechte): `/audit`, `/audit/ops`

### Profil: `audit_reader` (z. B. via `common.view_auditevent`)

- **Erwartete Audit-Permissions**
  - `audit.events.read`
- **Nicht erwartet**
  - `audit.ops.manage` (wenn kein Operator-Grant vorhanden)
- **Erwartete Navigation**
  - sichtbar: `/audit`
  - nicht sichtbar: `/audit/ops`

### Profil: `audit_operator` (z. B. via `common.operate_auditevent`)

- **Erwartete Audit-Permissions**
  - `audit.events.read` (indirekt ueber Reader-Logik moeglich, je nach Rollensetup)
  - `audit.ops.manage`
- **Erwartete Feature-Flags**
  - `audit_ops_enabled`
- **Erwartete Navigation**
  - sichtbar: `/audit`, `/audit/ops`

### Profil: `staff` (is_staff = true)

- **Erwartete Zusatz-Permissions**
  - `tenant.members.manage`
  - `tenant.settings.manage`
- **Audit-Hinweis**
  - Audit-Sichtbarkeit ist weiterhin an Audit-Checks gebunden (`is_audit_reader` / `is_audit_operator`).
- **Erwartete Navigation**
  - immer sichtbar: `/`, `/reports`, `/settings`
  - `/audit`, `/audit/ops` nur bei vorhandenen Audit-Permissions

## Sicherheitsgrenze

Frontend-Gating ist UX-Steuerung. Die Sicherheitsgrenze bleibt im Backend:

- DRF-Permissions und Service-Checks entscheiden final ueber Zugriff.
- Jede sensitive Operation braucht serverseitige Authorisierung.
