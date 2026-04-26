from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable machine-readable error identifiers sent to clients.

    Once a value is shipped, never rename it. Add new variants instead.
    Frontends switch on these to localize messages or branch UI.
    """

    INTERNAL_ERROR = "internal_error"
    VALIDATION_FAILED = "validation_failed"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    ALREADY_EXISTS = "already_exists"
    UNAUTHENTICATED = "unauthenticated"
    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"
    INVALID_TOKEN = "invalid_token"


class AppError(Exception):
    """Base class for all application exceptions.

    Subclasses override `status_code`, `code`, and `detail` as class attributes.
    `code` is a stable machine-readable identifier clients can switch on.
    `detail` is the human-readable message kept for server-side logging only;
    it is not sent over the wire.
    Pass a string to `__init__` to override the default detail for a single raise site.
    """

    status_code: int = 500
    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    detail: str = "Internal error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code: int = 404
    code: ErrorCode = ErrorCode.NOT_FOUND
    detail: str = "Not found"


class AlreadyExists(AppError):
    status_code: int = 409
    code: ErrorCode = ErrorCode.ALREADY_EXISTS
    detail: str = "Already exists"


class InvalidCredentials(AppError):
    status_code: int = 401
    code: ErrorCode = ErrorCode.INVALID_CREDENTIALS
    detail: str = "Invalid credentials"


class TokenExpired(AppError):
    status_code: int = 401
    code: ErrorCode = ErrorCode.TOKEN_EXPIRED
    detail: str = "Token expired"


class InvalidToken(AppError):
    status_code: int = 401
    code: ErrorCode = ErrorCode.INVALID_TOKEN
    detail: str = "Invalid token"
