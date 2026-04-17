# Audit Interfaces (`apps/common`)

## Zweck

Zentrale Referenz für operative Audit-Schnittstellen (Management-Commands und Operator-API).
Andere Audit-Dokumente verlinken hierher, um Duplikate zu vermeiden.

## Management-Commands

- `python manage.py audit_archive_events --before-days <n>`
- `python manage.py audit_archive_events --use-retention-policy`
- `python manage.py audit_export_siem --limit <n> [--mark-exported]`
- `python manage.py audit_backfill_integrity_hashes [--dry-run] [--limit <n>]`
- `python manage.py audit_verify_integrity [--create-checkpoint] [--limit <n>]`
- `python manage.py audit_health_snapshot --window-hours <n>`
- `python manage.py audit_setup_roles`

## Operator-API (`AuditOperationsViewSet`)

- `GET /api/common/v1/audit-ops/health-snapshot/`
- `POST /api/common/v1/audit-ops/verify-integrity/`
- `GET /api/common/v1/audit-ops/siem-export-preview/`
- `POST /api/common/v1/audit-ops/archive-events/`
- `POST /api/common/v1/audit-ops/setup-roles/`

## Limit- und Last-Hinweise

- `verify-integrity` akzeptiert optional `limit`; Werte sind serverseitig begrenzt.
- Für große Datenmengen bevorzugt mit `limit` arbeiten und periodische Verifikation automatisieren.
- SIEM-Preview/Export mit konservativen Batch-Größen planen und Monitoring auf Fehlerraten ergänzen.
