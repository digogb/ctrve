from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.core.deps import get_current_user, get_session, require_role
from app.models.user import User, UserRole
from app.schemas.checklist import ChecklistCreate, ChecklistEntregaUpdate, ChecklistResponse
from app.services.checklist_service import (
    create_checklist,
    get_checklist_by_id,
    search_checklists,
    update_entrega,
)

router = APIRouter(prefix="/checklists", tags=["checklists"])


@router.get("", response_model=list[ChecklistResponse])
def search(
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(get_current_user)],
    placa: str | None = None,
):
    return search_checklists(session, placa)


@router.get("/{checklist_id}", response_model=ChecklistResponse)
def get_one(
    checklist_id: int,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(get_current_user)],
):
    return get_checklist_by_id(session, checklist_id)


@router.patch("/{checklist_id}/entrega", response_model=ChecklistResponse)
def patch_entrega(
    checklist_id: int,
    body: ChecklistEntregaUpdate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    return update_entrega(session, checklist_id, body)


@router.post("", response_model=ChecklistResponse, status_code=status.HTTP_201_CREATED)
def create(
    body: ChecklistCreate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    return create_checklist(session, body)
