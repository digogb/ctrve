from pydantic import BaseModel

from app.models.user import UserRole


class UserCreate(BaseModel):
    username: str
    full_name: str
    matricula: str
    password: str
    role: UserRole = UserRole.motorista


class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    matricula: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
