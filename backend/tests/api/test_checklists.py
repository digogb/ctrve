"""Testes para criação de checklist (RN-005, RN-006, RN-007, RN-008)."""
from app.core.security import create_access_token
from app.models.checklist import Checklist, ChecklistStatus
from app.models.user import UserRole

VALID_CHECKLIST = {
    "placa": "ABC1D23",
    "unidade": "SECLOG",
    "motorista": "João Silva",
    "matricula_motorista": "123456",
    "quilometragem_inicial": 50000.0,
}


def _headers(test_user) -> dict:
    token = create_access_token({"sub": test_user.username, "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


def test_create_checklist_success(client, test_user):
    response = client.post(
        "/api/v1/checklists",
        json=VALID_CHECKLIST,
        headers=_headers(test_user),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["placa"] == "ABC1D23"
    assert data["status"] == "entregue"
    assert data["is_locked"] is False
    assert "id" in data


def test_create_checklist_placa_antiga(client, test_user):
    """RN-006: formato antigo ABC-1234 é aceito."""
    response = client.post(
        "/api/v1/checklists",
        json={**VALID_CHECKLIST, "placa": "ABC-1234"},
        headers=_headers(test_user),
    )
    assert response.status_code == 201
    assert response.json()["placa"] == "ABC-1234"


def test_create_checklist_placa_invalida(client, test_user):
    """RN-006: placa fora dos formatos retorna MSG-006."""
    response = client.post(
        "/api/v1/checklists",
        json={**VALID_CHECKLIST, "placa": "12345"},
        headers=_headers(test_user),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "MSG-006"
    assert "placa" in response.json()["fields"]


def test_create_checklist_matricula_nao_numerica(client, test_user):
    """RN-007: matrícula com letras retorna MSG-007."""
    response = client.post(
        "/api/v1/checklists",
        json={**VALID_CHECKLIST, "matricula_motorista": "ABC123"},
        headers=_headers(test_user),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "MSG-007"
    assert "matricula_motorista" in response.json()["fields"]


def test_create_checklist_entrega_duplicada(client, test_user, session):
    """RN-008: segunda entrega com mesma placa (locked) retorna MSG-008."""
    existing = Checklist(
        placa="ABC1D23",
        unidade="SECLOG",
        motorista="Outro Motorista",
        matricula_motorista="999999",
        quilometragem_inicial=40000,
        status=ChecklistStatus.entregue,
        is_locked=True,
    )
    session.add(existing)
    session.commit()

    response = client.post(
        "/api/v1/checklists",
        json=VALID_CHECKLIST,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-008"
    assert "placa" in response.json()["fields"]


def test_create_checklist_permite_apos_devolucao(client, test_user, session):
    """RN-008: entrega devolvida não bloqueia nova entrega."""
    existing = Checklist(
        placa="ABC1D23",
        unidade="SECLOG",
        motorista="Motorista Anterior",
        matricula_motorista="111111",
        quilometragem_inicial=40000,
        status=ChecklistStatus.devolvido,
        is_locked=True,
    )
    session.add(existing)
    session.commit()

    response = client.post(
        "/api/v1/checklists",
        json=VALID_CHECKLIST,
        headers=_headers(test_user),
    )
    assert response.status_code == 201


def test_create_checklist_subunidade_opcional(client, test_user):
    """AC-1: subunidade é opcional."""
    response = client.post(
        "/api/v1/checklists",
        json={**VALID_CHECKLIST, "subunidade": None},
        headers=_headers(test_user),
    )
    assert response.status_code == 201
    assert response.json()["subunidade"] is None


def test_create_checklist_motorista_proibido(client, session):
    """AC-7: motorista não pode criar checklist — retorna MSG-026."""
    from app.models.user import User
    motorista = User(
        username="motorista_test",
        full_name="Motorista",
        matricula="777777",
        hashed_password="x",
        role=UserRole.motorista,
    )
    session.add(motorista)
    session.commit()
    token = create_access_token({"sub": "motorista_test", "role": UserRole.motorista})
    response = client.post(
        "/api/v1/checklists",
        json=VALID_CHECKLIST,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "MSG-026"
