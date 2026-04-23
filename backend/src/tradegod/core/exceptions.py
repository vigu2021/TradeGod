class AppError(Exception):
    """Base class for all application exceptions.

    Subclasses override `status_code` and `detail` as class attributes.
    Pass a string to `__init__` to override the default detail for a single raise site.
    """

    status_code: int = 500
    detail: str = "Internal error"

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code: int = 404
    detail: str = "Not found"


class AlreadyExists(AppError):
    status_code: int = 409
    detail: str = "Already exists"


class InvalidCredentials(AppError):
    status_code: int = 401
    detail: str = "Invalid credentials"


class TokenExpired(AppError):
    status_code: int = 401
    detail: str = "Token expired"


class InvalidToken(AppError):
    status_code: int = 401
    detail: str = "Invalid token"
