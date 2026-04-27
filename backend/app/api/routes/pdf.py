import re
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlmodel import Session

from app.core.deps import get_current_user, get_session
from app.models.user import User
from app.services.checklist_service import ChecklistError, get_checklist_by_id
from app.services.pdf_service import generate_checklist_pdf

router = APIRouter(prefix="/checklists", tags=["pdf"])

_SAFE_DATA_URI = re.compile(r"^data:image/[a-zA-Z+]+;base64,[A-Za-z0-9+/=]+$")


@router.get("/{checklist_id}/pdf")
def download_pdf(
    checklist_id: int,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(get_current_user)],
):
    checklist = get_checklist_by_id(session, checklist_id)
    if not checklist.is_locked:
        raise ChecklistError(
            status_code=400,
            detail="MSG-019",
            message="As opções de compartilhamento e impressão estarão disponíveis após o salvamento do checklist.",
            fields=[],
        )
    sig_fields = [
        checklist.assinatura_responsavel,
        checklist.assinatura_motorista,
        checklist.assinatura_responsavel_devolucao,
        checklist.assinatura_motorista_devolucao,
    ]
    if any(f is not None and not _SAFE_DATA_URI.match(f) for f in sig_fields):
        raise ChecklistError(
            status_code=400,
            detail="ASSINATURA_INVALIDA",
            message="Formato de assinatura inválido.",
            fields=[],
        )
    pdf_bytes = generate_checklist_pdf(checklist)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="checklist-{checklist_id}.pdf"',
        },
    )
