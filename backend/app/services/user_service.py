import re

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


class UserError(Exception):
    def __init__(self, status_code: int, detail: str, message: str, fields: list[str] | None = None):
        self.status_code = status_code
        self.detail = detail
        self.message = message
        self.fields = fields or []


def create_user(session: Session, data: UserCreate) -> User:
    # P-6: validar senha antes de qualquer roundtrip ao BD
    # P-1: fullmatch para ancorar no fim da string (evita bypass com \n)
    if not PASSWORD_REGEX.fullmatch(data.password):
        raise UserError(
            status_code=422,
            detail="MSG-004",
            message="A senha deve conter no mínimo 8 caracteres, incluindo ao menos uma letra maiúscula, uma letra minúscula e um número.",
            fields=["password"],
        )

    # P-4: bloquear criação de Responsável até existir role de admin
    if data.role == UserRole.responsavel:
        raise UserError(
            status_code=403,
            detail="MSG-026",
            message="Apenas administradores podem criar usuários com perfil Responsável.",
            fields=["role"],
        )

    # P-3: verificar unicidade de username a nível de aplicação
    existing_username = session.exec(
        select(User).where(User.username == data.username)
    ).first()
    if existing_username:
        raise UserError(
            status_code=400,
            detail="ERR-USERNAME-DUPLICATE",
            message="O nome de usuário informado já está em uso.",
            fields=["username"],
        )

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

    user = User(
        username=data.username,
        full_name=data.full_name,
        matricula=data.matricula,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    session.add(user)
    # P-2: capturar IntegrityError de inserções concorrentes
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise UserError(
            status_code=400,
            detail="MSG-003",
            message="Conflito ao cadastrar usuário — matrícula ou nome de usuário já existente.",
            fields=["matricula", "username"],
        )
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()
