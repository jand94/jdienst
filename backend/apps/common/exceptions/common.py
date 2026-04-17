from apps.common.constants import ErrorCode


class CommonError(Exception):
    code = ErrorCode.COMMON_ERROR
    status_code = 500
    default_message = "An unexpected error occurred."

    def __init__(self, message: str | None = None, *, details: dict | None = None):
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CommonError):
    code = ErrorCode.VALIDATION_ERROR
    status_code = 400
    default_message = "The request data is invalid."


class ConflictError(CommonError):
    code = ErrorCode.CONFLICT_ERROR
    status_code = 409
    default_message = "The request conflicts with current state."


class InfrastructureError(CommonError):
    code = ErrorCode.INFRASTRUCTURE_ERROR
    status_code = 503
    default_message = "A dependent infrastructure component is unavailable."


class SecurityError(CommonError):
    code = ErrorCode.SECURITY_ERROR
    status_code = 403
    default_message = "The requested operation is not permitted."
