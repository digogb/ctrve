from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

DUMMY_HASH = b"$2b$12$6H4E8g1vgO2.RkUNG4tWaugsWfmosg4cmBFQ5.6Njku1GFRGj47hK"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password_safe(plain: str, hashed: str | None) -> bool:
    """Always runs bcrypt to prevent timing attacks on user enumeration."""
    if hashed is None:
        bcrypt.checkpw(plain.encode(), DUMMY_HASH)
        return False
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload["exp"] = expire
    payload["type"] = "access"
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    payload["exp"] = expire
    payload["type"] = "refresh"
    payload["jti"] = str(uuid4())
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str, token_type: str = "access") -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != token_type:
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise
