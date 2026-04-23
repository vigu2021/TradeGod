import asyncio
import hashlib
import secrets
from datetime import datetime, UTC, timedelta
from typing import Final

import jwt

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import SecretStr
from tradegod.core.settings import get_settings

SECRET_KEY: Final[SecretStr] = get_settings().jwt_secret
_ph: Final[PasswordHasher] = PasswordHasher()


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


def create_access_token(user_id: int) -> str:
    expires_at = datetime.now(UTC) + timedelta(minutes=30)
    payload = {"sub": str(user_id), "exp": expires_at, "type": "access"}
    return jwt.encode(payload, SECRET_KEY.get_secret_value(), algorithm="HS256")
