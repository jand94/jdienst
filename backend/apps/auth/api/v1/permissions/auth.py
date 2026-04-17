from rest_framework.permissions import IsAuthenticated


class IsAuthenticatedForAuthMutation(IsAuthenticated):
    message = "Authentication is required for this operation."
