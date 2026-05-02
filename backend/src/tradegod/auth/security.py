import asyncio
import hashlib
import secrets
from datetime import datetime, UTC, timedelta
from typing import Final, Literal, TypedDict, cast

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from tradegod.auth.exceptions import InvalidToken, TokenExpired
from tradegod.core.settings import get_settings

ALGORITHM: Final[str] = "HS256"

_ph: Final[PasswordHasher] = PasswordHasher()


class AccessTokenPayload(TypedDict):
    sub: str
    iat: int
    exp: int
    type: Literal["access"]


async def hash_password(raw_password: str) -> str:
    """Hash with argon2 on a worker thread so the event loop stays responsive."""
    return await asyncio.to_thread(_ph.hash, raw_password)


async def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Verify a password against its argon2 hash on a worker thread.

    Returns False on mismatch. Other argon2 errors (e.g. corrupted hash)
    propagate so callers can distinguish bad credentials from bad data.
    """
    try:
        return await asyncio.to_thread(_ph.verify, hashed_password, raw_password)
    except VerifyMismatchError:
        return False


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=get_settings().access_token_expire_minutes)
    payload: AccessTokenPayload = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "type": "access",
    }
    return jwt.encode(payload, get_settings().jwt_secret.get_secret_value(), algorithm=ALGORITHM)  # pyright: ignore[reportArgumentType]


def decode_access_token(token: str) -> AccessTokenPayload:
    """Verify an access token's signature/expiry and return its typed payload.

    @throws TokenExpired if the token is past its exp claim.
    @throws InvalidToken if the signature is bad, the token is malformed, or
        the `type` claim is not "access".
    """
    try:
        payload = jwt.decode(token, get_settings().jwt_secret.get_secret_value(), algorithms=[ALGORITHM])
    except ExpiredSignatureError as e:
        raise TokenExpired from e
    except InvalidTokenError as e:
        raise InvalidToken from e

    if payload.get("type") != "access":
        raise InvalidToken("Token is not an access token")

    return cast(AccessTokenPayload, payload)  # pyright: ignore[reportInvalidCast]
