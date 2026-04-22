from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.deps import get_session, require_role
from app.models.user import User, UserRole
from app.schemas.checklist import ChecklistCreate, ChecklistResponse
from app.services.checklist_service import create_checklist

router = APIRouter(prefix="/checklists", tags=["checklists"])


@router.post("", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
def create(
    body: ChecklistCreate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    return create_checklist(session, body)
