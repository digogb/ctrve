from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.checklist import ChecklistStatus
from app.schemas.damage import DamagePointData


class ChecklistCreate(BaseModel):
    placa: str
    unidade: str
    subunidade: str | None = None
    motorista: str
    matricula_motorista: str
    quilometragem_inicial: float


class ChecklistItemData(BaseModel):
    nome: str
    status: Literal["ok", "nao_ok"] | None = None


class ChecklistEntregaUpdate(BaseModel):
    itens: list[ChecklistItemData]
    nivel_combustivel: Literal["1/4", "2/4", "3/4", "4/4"]
    data_entrega: datetime
    avarias: list[DamagePointData] | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validate_itens(self) -> "ChecklistEntregaUpdate":
        if len(self.itens) != 20:
            raise ValueError(
                f"Exatamente 20 itens são obrigatórios; recebidos: {len(self.itens)}"
            )
        null_items = [item.nome for item in self.itens if item.status is None]
        if null_items:
            raise ValueError(
                f"Todos os itens devem ter status 'ok' ou 'nao_ok': {null_items}"
            )
        return self


class ChecklistResponse(BaseModel):
    id: int
    placa: str
    unidade: str
    subunidade: str | None
    motorista: str
    matricula_motorista: str
    quilometragem_inicial: float
    status: ChecklistStatus
    is_locked: bool
    itens: list[ChecklistItemData] | None = None
    nivel_combustivel: Literal["1/4", "2/4", "3/4", "4/4"] | None = None
    data_entrega: datetime | None = None
    avarias: list[DamagePointData] | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
