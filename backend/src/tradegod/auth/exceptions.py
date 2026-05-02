from tradegod.core.exceptions import AppError, ErrorCode


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
