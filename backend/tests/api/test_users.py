"""Testes para cadastro de usuário e /users/me (RN-003, RN-004)."""
import pytest
from app.core.security import create_access_token
from app.models.user import UserRole


VALID_USER = {
    "username": "novousuario",
    "full_name": "Novo Usuário",
    "matricula": "999999",
    "password": "Senha123",
    "role": "motorista",
}


def _responsavel_headers(test_user) -> dict:
    token = create_access_token({"sub": test_user.username, "role": test_user.role})
    return {"Authorization": f"Bearer {token}"}


def test_create_user_success(client, test_user):
    response = client.post(
        "/api/v1/users",
        json=VALID_USER,
        headers=_responsavel_headers(test_user),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "novousuario"
    assert data["matricula"] == "999999"
    assert data["role"] == "motorista"
    assert "hashed_password" not in data


def test_create_user_duplicate_matricula(client, test_user):
    """RN-003: matrícula duplicada retorna MSG-003."""
    client.post(
        "/api/v1/users",
        json=VALID_USER,
        headers=_responsavel_headers(test_user),
    )
    response = client.post(
        "/api/v1/users",
        json={**VALID_USER, "username": "outro"},
        headers=_responsavel_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-003"
    assert "matricula" in response.json()["fields"]


def test_create_user_weak_password_no_uppercase(client, test_user):
    """RN-004: senha sem maiúscula retorna MSG-004."""
    response = client.post(
        "/api/v1/users",
        json={**VALID_USER, "password": "senha123"},
        headers=_responsavel_headers(test_user),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "MSG-004"
    assert "password" in response.json()["fields"]


def test_create_user_weak_password_too_short(client, test_user):
    """RN-004: senha curta retorna MSG-004."""
    response = client.post(
        "/api/v1/users",
        json={**VALID_USER, "password": "Se1"},
        headers=_responsavel_headers(test_user),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "MSG-004"


def test_create_user_weak_password_no_number(client, test_user):
    """RN-004: senha sem número retorna MSG-004."""
    response = client.post(
        "/api/v1/users",
        json={**VALID_USER, "password": "SenhaForte"},
        headers=_responsavel_headers(test_user),
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "MSG-004"


def test_create_user_requires_responsavel(client, session, test_user):
    """AC-5: motorista não pode cadastrar usuários — retorna MSG-026."""
    from app.models.user import User, UserRole
    motorista = User(
        username="motorista1",
        full_name="Motorista",
        matricula="111111",
        hashed_password="x",
        role=UserRole.motorista,
    )
    session.add(motorista)
    session.commit()
    token = create_access_token({"sub": "motorista1", "role": UserRole.motorista})
    response = client.post(
        "/api/v1/users",
        json=VALID_USER,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "MSG-026"


def test_create_user_unauthenticated(client):
    response = client.post("/api/v1/users", json=VALID_USER)
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    response = client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["role"] == "responsavel"


def test_get_me_unauthenticated(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
