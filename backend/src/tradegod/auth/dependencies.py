from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from tradegod.auth.security import decode_access_token


# Validate auth token and get the user
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user_id(access_token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    payload = decode_access_token(access_token)
    return int(payload["sub"])


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
