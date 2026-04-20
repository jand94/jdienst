from rest_framework.permissions import IsAuthenticated


class IsTaskUser(IsAuthenticated):
    message = "Authentication is required for task operations."
