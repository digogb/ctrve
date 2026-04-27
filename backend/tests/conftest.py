import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

_VALID_SIGNATURE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
_ITEM_NAMES = [
    "Documento Veicular", "Chave de Roda", "Macaco", "Triângulo de Sinalização",
    "Estepe", "Extintor de Incêndio", "Cintos de Segurança", "Luzes de Freios",
    "Nível de água (aditivo)", "Óleo de motor",
    "Luzes de Posição (faroletes)", "Faróis (alto e baixo)", "Luzes de Seta (pisca-alerta)",
    "Luz de Placa", "Luz de Ré", "Ar Condicionado", "Buzina",
    "Rádio/Multimídia", "Fluidos de Freios", "Limpadores de Para-brisa",
]

from app.core.config import settings
from app.core.security import hash_password
from app.database import get_session
from app.main import app
from app.models.user import User, UserRole


@pytest.fixture(autouse=True, scope="session")
def force_debug_mode():
    """TestClient usa HTTP — cookies Secure=True seriam descartados. DEBUG=True força Secure=False."""
    original = settings.DEBUG
    settings.DEBUG = True
    yield
    settings.DEBUG = original


@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    user = User(
        username="testuser",
        full_name="Usuário Teste",
        matricula="123456",
        hashed_password=hash_password("Senha123"),
        role=UserRole.responsavel,
        is_active=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Senha123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(name="checklist_abc1d23")
def checklist_abc1d23_fixture(session):
    from app.models.checklist import Checklist

    c = Checklist(
        placa="ABC1D23",
        unidade="SECLOG",
        motorista="João Silva",
        matricula_motorista="123456",
        quilometragem_inicial=10000.0,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@pytest.fixture(name="checklist_entrega_payload")
def checklist_entrega_payload_fixture():
    from datetime import datetime, timezone

    return {
        "itens": [{"nome": nome, "status": "ok"} for nome in _ITEM_NAMES],
        "nivel_combustivel": "3/4",
        "data_entrega": datetime.now(timezone.utc).isoformat(),
        "assinatura_responsavel": _VALID_SIGNATURE,
        "assinatura_motorista": _VALID_SIGNATURE,
    }


@pytest.fixture(name="locked_checklist")
def locked_checklist_fixture(session):
    from datetime import datetime, timezone
    from app.models.checklist import Checklist, ChecklistStatus

    c = Checklist(
        placa="ABC1D23",
        unidade="SECLOG",
        motorista="João Silva",
        matricula_motorista="123456",
        quilometragem_inicial=50000.0,
        status=ChecklistStatus.entregue,
        is_locked=True,
        itens=[{"nome": nome, "status": "ok"} for nome in _ITEM_NAMES],
        nivel_combustivel="3/4",
        data_entrega=datetime(2026, 4, 20, 10, 0, tzinfo=timezone.utc),
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c


@pytest.fixture(name="checklist_devolucao_payload")
def checklist_devolucao_payload_fixture():
    from datetime import datetime, timezone

    return {
        "itens": [{"nome": nome, "status": "ok"} for nome in _ITEM_NAMES],
        "nivel_combustivel": "2/4",
        "quilometragem_final": 51000.0,
        "data_devolucao": datetime(2026, 4, 23, 14, 0, tzinfo=timezone.utc).isoformat(),
        "assinatura_responsavel": _VALID_SIGNATURE,
        "assinatura_motorista": _VALID_SIGNATURE,
    }


@pytest.fixture(name="motorista_headers")
def motorista_headers_fixture(client, session):
    motorista = User(
        username="motorista_test",
        full_name="Motorista Teste",
        matricula="999999",
        hashed_password=hash_password("Senha123"),
        role=UserRole.motorista,
        is_active=True,
    )
    session.add(motorista)
    session.commit()
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "motorista_test", "password": "Senha123"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
