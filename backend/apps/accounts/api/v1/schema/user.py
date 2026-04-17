from drf_spectacular.utils import extend_schema, extend_schema_view


account_user_viewset_schema = extend_schema_view(
    list=extend_schema(
        tags=["Accounts - User"],
        summary="List users (staff only)",
    ),
    retrieve=extend_schema(
        tags=["Accounts - User"],
        summary="Retrieve user profile by id",
    ),
    update=extend_schema(
        tags=["Accounts - User"],
        summary="Update user profile by id",
    ),
    partial_update=extend_schema(
        tags=["Accounts - User"],
        summary="Partially update own user profile",
    ),
    me=extend_schema(
        tags=["Accounts - User - Self Service"],
        summary="Retrieve authenticated user profile",
    ),
    deactivate_me=extend_schema(
        tags=["Accounts - User - Self Service"],
        summary="Deactivate authenticated user",
    ),
)
