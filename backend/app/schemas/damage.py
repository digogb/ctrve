from typing import Literal

from pydantic import BaseModel, Field


class DamagePointData(BaseModel):
    model_config = {"json_schema_extra": {"examples": [{"x": 50.0, "y": 30.0, "vista": "topo", "tipo": "risco"}]}}

    x: float = Field(ge=0, le=100)
    y: float = Field(ge=0, le=100)
    vista: Literal["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"]
    tipo: Literal["risco", "amassado", "trincado"]
