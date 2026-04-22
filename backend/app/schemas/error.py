from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    message: str
    fields: list[str] = []
