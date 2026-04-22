from datetime import datetime

from pydantic import BaseModel

from app.models.checklist import ChecklistStatus


class ChecklistCreate(BaseModel):
    placa: str
    unidade: str
    subunidade: str | None = None
    motorista: str
    matricula_motorista: str
    quilometragem_inicial: float


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
    created_at: datetime

    model_config = {"from_attributes": True}
