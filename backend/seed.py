"""Seed inicial: cria usuários padrão se ainda não existirem."""
from app.core.security import hash_password
from app.database import create_db_and_tables, engine
from app.models.user import User, UserRole
from sqlmodel import Session, select

USERS = [
    {
        "username": "responsavel",
        "full_name": "Responsável Padrão",
        "matricula": "0001",
        "password": "Senha123",
        "role": UserRole.responsavel,
    },
    {
        "username": "motorista",
        "full_name": "Motorista Padrão",
        "matricula": "0002",
        "password": "Senha123",
        "role": UserRole.motorista,
    },
]


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        for data in USERS:
            exists = session.exec(
                select(User).where(User.username == data["username"])
            ).first()
            if exists:
                print(f"[skip] {data['username']} já existe")
                continue
            user = User(
                username=data["username"],
                full_name=data["full_name"],
                matricula=data["matricula"],
                hashed_password=hash_password(data["password"]),
                role=data["role"],
            )
            session.add(user)
            session.commit()
            print(f"[ok]   {data['username']} ({data['role']}) criado")


if __name__ == "__main__":
    seed()
