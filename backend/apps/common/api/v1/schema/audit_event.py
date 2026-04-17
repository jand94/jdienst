from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema, extend_schema_view


audit_event_viewset_schema = extend_schema_view(
    list=extend_schema(
        tags=["Audit - Events"],
        summary="Listet Audit-Events read-only",
        parameters=[
            OpenApiParameter(
                name="action",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtert nach exakter Action.",
            ),
            OpenApiParameter(
                name="target_model",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtert nach Django Label, z. B. accounts.User.",
            ),
            OpenApiParameter(
                name="target_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtert nach Target-ID.",
            ),
        ],
    ),
    retrieve=extend_schema(
        tags=["Audit - Events"],
        summary="Liefert ein einzelnes Audit-Event read-only",
    ),
)
