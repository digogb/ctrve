from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.deps import get_current_user, get_session, require_role
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import create_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    body: UserCreate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    return create_user(session, body)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
