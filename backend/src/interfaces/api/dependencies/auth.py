from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from jwt import InvalidTokenError
from starlette import status

from src.application.services.auth import ALGORITHM, oauth2_scheme
from src.infrastructure.repositories.user import UserRepo
from src.infrastructure.schemas.user import TokenData
from src.settings import settings


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], repo: UserRepo = Depends()
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.app.secret_key, algorithms=[ALGORITHM]
        )
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except InvalidTokenError:
        raise credentials_exception
    user = await repo.get(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user
