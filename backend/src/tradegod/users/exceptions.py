from tradegod.core.exceptions import AppError, ErrorCode


class AlreadyExists(AppError):
    status_code: int = 409
    code: ErrorCode = ErrorCode.ALREADY_EXISTS
    detail: str = "Already exists"
