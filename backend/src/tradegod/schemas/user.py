from datetime import datetime

from pydantic import EmailStr

from tradegod.schemas.base import PublicModel


class UserPublic(PublicModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
