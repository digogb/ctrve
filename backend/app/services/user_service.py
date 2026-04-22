import re

from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


class UserError(Exception):
    def __init__(self, status_code: int, detail: str, message: str, fields: list[str] | None = None):
        self.status_code = status_code
        self.detail = detail
        self.message = message
        self.fields = fields or []


def create_user(session: Session, data: UserCreate) -> User:
    existing = session.exec(
        select(User).where(User.matricula == data.matricula)
    ).first()
    if existing:
        raise UserError(
            status_code=400,
            detail="MSG-003",
            message="A matrícula informada já está cadastrada no sistema. Verifique o número e tente novamente.",
            fields=["matricula"],
        )

    if not PASSWORD_REGEX.match(data.password):
        raise UserError(
            status_code=422,
            detail="MSG-004",
            message="A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número.",
            fields=["password"],
        )

    user = User(
        username=data.username,
        full_name=data.full_name,
        matricula=data.matricula,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()
