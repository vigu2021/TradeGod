from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tradegod.core.exceptions import AlreadyExists
from tradegod.models import User


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, email: str, hashed_password: str) -> User:
    user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(user)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise AlreadyExists("This username or email already exists")
    return user
