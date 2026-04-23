from datetime import datetime, timezone
from enum import Enum
from typing import Any

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel


class ChecklistStatus(str, Enum):
    entregue = "entregue"
    devolvido = "devolvido"


class Checklist(SQLModel, table=True):
    __tablename__ = "checklists"

    id: int | None = Field(default=None, primary_key=True)
    placa: str = Field(index=True)
    unidade: str
    subunidade: str | None = None
    motorista: str
    matricula_motorista: str
    quilometragem_inicial: float
    status: ChecklistStatus = Field(default=ChecklistStatus.entregue)
    is_locked: bool = Field(default=False)
    itens: list[Any] | None = Field(default=None, sa_column=Column(JSON))
    avarias: list[Any] | None = Field(default=None, sa_column=Column(JSON))
    nivel_combustivel: str | None = None
    data_entrega: datetime | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
