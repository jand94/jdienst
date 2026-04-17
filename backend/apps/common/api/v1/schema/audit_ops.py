from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view


audit_ops_viewset_schema = extend_schema_view(
    health_snapshot=extend_schema(
        tags=["Common - Audit Operations - Monitoring"],
        summary="Liefert Audit-Health-Snapshot",
        parameters=[
            OpenApiParameter(
                name="window_hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Zeitfenster fuer Snapshot in Stunden (1-720).",
            ),
        ],
    ),
    verify_integrity=extend_schema(
        tags=["Common - Audit Operations - Integrity"],
        summary="Startet Integritaets-Verifikation und optionalen Checkpoint",
    ),
    siem_export_preview=extend_schema(
        tags=["Common - Audit Operations - SIEM"],
        summary="Zeigt SIEM-Exportvorschau ohne Export-Markierung",
        parameters=[
            OpenApiParameter(
                name="limit",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Maximale Anzahl Vorschau-Events (1-500).",
            ),
        ],
    ),
    archive_events=extend_schema(
        tags=["Common - Audit Operations - Retention"],
        summary="Startet Audit-Archivierung (Tage-basiert oder Retention-Policy)",
    ),
    setup_roles=extend_schema(
        tags=["Common - Audit Operations - Access"],
        summary="Synchronisiert konfigurierte Audit-Reader-Rollen",
    ),
)
