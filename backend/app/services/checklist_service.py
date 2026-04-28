import re

from sqlalchemy import desc
from sqlmodel import Session, select

from app.models.checklist import Checklist, ChecklistStatus
from app.schemas.checklist import ChecklistCreate, ChecklistDevolucaoUpdate, ChecklistEntregaUpdate

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


def get_checklist_by_id(session: Session, checklist_id: int) -> Checklist:
    checklist = session.get(Checklist, checklist_id)
    if not checklist:
        raise ChecklistError(
            status_code=404,
            detail="NOT_FOUND",
            message="Checklist não encontrado.",
            fields=[],
        )
    return checklist


def cancel_checklist(session: Session, checklist_id: int) -> None:
    checklist = get_checklist_by_id(session, checklist_id)
    if checklist.is_locked:
        raise ChecklistError(
            status_code=400,
            detail="LOCKED",
            message="Checklist bloqueado não pode ser cancelado.",
            fields=[],
        )
    session.delete(checklist)
    session.commit()


def search_checklists(session: Session, placa: str | None = None) -> list[Checklist]:
    query = select(Checklist)
    if placa:
        query = query.where(Checklist.placa.contains(placa.upper(), autoescape=True))
    query = query.order_by(desc(Checklist.created_at))
    return list(session.exec(query).all())


def update_entrega(session: Session, checklist_id: int, data: ChecklistEntregaUpdate) -> Checklist:
    checklist = session.get(Checklist, checklist_id)
    if not checklist:
        raise ChecklistError(
            status_code=404,
            detail="NOT_FOUND",
            message="Checklist não encontrado.",
            fields=[],
        )
    if checklist.status == ChecklistStatus.devolvido:
        raise ChecklistError(
            status_code=400,
            detail="INVALID_STATUS",
            message="Checklist já devolvido não pode ter a entrega atualizada.",
            fields=["status"],
        )
    if checklist.is_locked:
        raise ChecklistError(
            status_code=400,
            detail="MSG-026",
            message="Checklist bloqueado e não pode ser alterado.",
            fields=[],
        )
    checklist.itens = [{"nome": item.nome, "status": item.status} for item in data.itens]
    checklist.nivel_combustivel = data.nivel_combustivel
    checklist.data_entrega = data.data_entrega
    if data.avarias is not None:
        checklist.avarias = [p.model_dump() for p in data.avarias]
    if data.assinatura_responsavel is not None:
        checklist.assinatura_responsavel = data.assinatura_responsavel
    if data.assinatura_motorista is not None:
        checklist.assinatura_motorista = data.assinatura_motorista
    if data.observacoes is not None:
        checklist.observacoes = data.observacoes
    checklist.status = ChecklistStatus.entregue
    checklist.is_locked = True
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist


def update_devolucao(session: Session, checklist_id: int, data: ChecklistDevolucaoUpdate) -> Checklist:
    checklist = session.get(Checklist, checklist_id)
    if not checklist:
        raise ChecklistError(
            status_code=404,
            detail="NOT_FOUND",
            message="Checklist não encontrado.",
            fields=[],
        )

    if not checklist.is_locked or checklist.status != ChecklistStatus.entregue:
        raise ChecklistError(
            status_code=400,
            detail="MSG-015",
            message=f"Não é possível iniciar a devolução. Não foi encontrada entrega concluída para o Nº de Controle {checklist.id}.",
            fields=[],
        )

    if data.quilometragem_final < checklist.quilometragem_inicial:
        raise ChecklistError(
            status_code=400,
            detail="MSG-016",
            message=f"A Quilometragem Final ({data.quilometragem_final}) não pode ser inferior à Quilometragem Inicial ({checklist.quilometragem_inicial}).",
            fields=["quilometragem_final"],
        )

    if checklist.data_entrega and data.data_devolucao.replace(tzinfo=None) < checklist.data_entrega.replace(tzinfo=None):
        raise ChecklistError(
            status_code=400,
            detail="MSG-017",
            message=f"A Data de Devolução não pode ser anterior à Data de Entrega ({checklist.data_entrega}).",
            fields=["data_devolucao"],
        )

    checklist.itens_devolucao = [{"nome": item.nome, "status": item.status} for item in data.itens]
    checklist.nivel_combustivel_devolucao = data.nivel_combustivel
    checklist.quilometragem_final = data.quilometragem_final
    checklist.data_devolucao = data.data_devolucao
    checklist.status = ChecklistStatus.devolvido

    if data.assinatura_responsavel is not None:
        checklist.assinatura_responsavel_devolucao = data.assinatura_responsavel
    if data.assinatura_motorista is not None:
        checklist.assinatura_motorista_devolucao = data.assinatura_motorista
    if data.observacoes is not None:
        checklist.observacoes_devolucao = data.observacoes

    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist


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

    # P-4: quilometragem não pode ser negativa
    if data.quilometragem_inicial < 0:
        raise ChecklistError(
            status_code=422,
            detail="VALIDATION_ERROR",
            message="A quilometragem inicial não pode ser negativa.",
            fields=["quilometragem_inicial"],
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
