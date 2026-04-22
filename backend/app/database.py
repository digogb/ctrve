from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings
import app.models.checklist  # noqa: F401 — garante que tabela é criada
import app.models.user  # noqa: F401

engine = create_engine(settings.DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
