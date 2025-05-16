import logging
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.responses import JSONResponse

from src.application.services.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_refresh_token,
)
from src.infrastructure.repositories.user import UserRepo
from src.infrastructure.schemas.user import Token

router = APIRouter(prefix="/users")
logger = logging.getLogger(__name__)


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: UserRepo = Depends(),
) -> Token:
    user = await authenticate_user(
        form_data.username, form_data.password, repo
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_token(
    refresh_token: str, repo: UserRepo = Depends()
) -> Token:

    user = await verify_refresh_token(refresh_token, repo)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return Token(
        access_token=new_access_token,
        refresh_token=refresh_token,
    )


@router.post("/")
async def create_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    repo: UserRepo = Depends(),
) -> JSONResponse:
    try:
        await repo.create(
            email=form_data.username,
            password=get_password_hash(form_data.password),
        )
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return JSONResponse(
        content={"status": "ok"}, status_code=status.HTTP_200_OK
    )
