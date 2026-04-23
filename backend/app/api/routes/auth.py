from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import JWTError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.deps import get_session
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password_safe,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _invalid_credentials() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="MSG-001",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _session_expired() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="MSG-002",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.username == body.username)).first()
    hashed = user.hashed_password if user else None

    if not verify_password_safe(body.password, hashed) or user is None or not user.is_active:
        raise _invalid_credentials()

    access_token = create_access_token({"sub": user.username, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.username})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
        max_age=60 * 60 * 24 * 7,
    )
    return TokenResponse(access_token=access_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    refresh_token: Annotated[str | None, Cookie()] = None,
):
    if not refresh_token:
        raise _session_expired()

    try:
        payload = decode_token(refresh_token, token_type="refresh")
        username: str | None = payload.get("sub")
        if not username:
            raise _session_expired()
    except JWTError:
        raise _session_expired()

    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not user.is_active:
        raise _session_expired()

    access_token = create_access_token({"sub": user.username, "role": user.role})
    new_refresh = create_refresh_token({"sub": user.username})

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
        max_age=60 * 60 * 24 * 7,
    )
    return TokenResponse(access_token=access_token)
