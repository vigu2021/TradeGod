from pydantic import EmailStr, Field, SecretStr

from tradegod.core.schemas import PublicModel
from tradegod.users.schemas import UserPublic


class RegisterRequest(PublicModel):
    username: str = Field(min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)


class LoginRequest(PublicModel):
    email: EmailStr
    password: SecretStr


class AccessToken(PublicModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(PublicModel):
    user: UserPublic
    tokens: AccessToken
