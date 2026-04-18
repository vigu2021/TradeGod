import asyncio
from typing import Final
from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.crud.user import create_user
from tradegod.models import User

_ph: Final[PasswordHasher] = PasswordHasher()


async def register_user(db: AsyncSession, username: str, email: str, raw_password: str) -> User:
    """Hash the password and persist a new user.

    Raises:
        AlreadyExists: if the username or email is already taken.
    """
    hashed_password = await _hash_password(raw_password)
    user = await create_user(db, username, email, hashed_password)
    return user


async def _hash_password(raw_password: str) -> str:
    """Hash with argon2 on a worker thread so the event loop stays responsive."""
    return await asyncio.to_thread(_ph.hash, raw_password)
