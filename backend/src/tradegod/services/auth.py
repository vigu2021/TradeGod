from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.security import hash_password
from tradegod.crud.user import create_user
from tradegod.models import User


async def register_user(db: AsyncSession, username: str, email: str, raw_password: str) -> User:
    """Hash the password and persist a new user.

    Raises:
        AlreadyExists: if the username or email is already taken.
    """
    hashed_password = await hash_password(raw_password)
    user = await create_user(db, username, email, hashed_password)
    return user
