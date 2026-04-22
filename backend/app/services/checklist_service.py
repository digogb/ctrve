import re

from sqlmodel import Session, select

from app.models.checklist import Checklist, ChecklistStatus
from app.schemas.checklist import ChecklistCreate

PLACA_REGEX = re.compile(r"^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}-[0-9]{4}$")


class ChecklistError(Exception):
    def __init__(
        self,
        status_code: int,
        detail: str,
        message: str,
        fields: list[str] | None = None,
    ):
        self.status_code = status_code
        self.detail = detail
        self.message = message
        self.fields = fields or []


def create_checklist(session: Session, data: ChecklistCreate) -> Checklist:
    # RN-006: formato de placa
    placa_upper = data.placa.upper()
    if not PLACA_REGEX.fullmatch(placa_upper):
        raise ChecklistError(
            status_code=422,
            detail="MSG-006",
            message="Formato de placa inválido. Informe no formato Mercosul (ABC1D23) ou antigo (ABC-1234).",
            fields=["placa"],
        )

    # RN-007: matrícula numérica
    if not data.matricula_motorista.isdigit():
        raise ChecklistError(
            status_code=422,
            detail="MSG-007",
            message="O campo Matrícula aceita apenas valores numéricos.",
            fields=["matricula_motorista"],
        )

    # RN-008: bloqueio de entrega duplicada
    open_delivery = session.exec(
        select(Checklist).where(
            Checklist.placa == placa_upper,
            Checklist.status == ChecklistStatus.entregue,
            Checklist.is_locked == True,  # noqa: E712
        )
    ).first()
    if open_delivery:
        raise ChecklistError(
            status_code=400,
            detail="MSG-008",
            message=f"Já existe um checklist de entrega aberto para o veículo de placa {placa_upper}. Conclua a devolução antes de registrar nova entrega.",
            fields=["placa"],
        )

    checklist = Checklist(
        placa=placa_upper,
        unidade=data.unidade,
        subunidade=data.subunidade,
        motorista=data.motorista,
        matricula_motorista=data.matricula_motorista,
        quilometragem_inicial=data.quilometragem_inicial,
    )
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist
