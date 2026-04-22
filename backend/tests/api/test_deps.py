"""Testes para get_current_user e require_role (RN-001, RN-002)."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.deps import get_current_user, get_session, require_role
from app.core.security import create_access_token
from app.models.user import User, UserRole


def _make_app(session: Session):
    """Monta app mínima para testar dependencies."""
    from fastapi import Depends
    from typing import Annotated

    app = FastAPI()

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session

    @app.get("/me")
    def me(user: Annotated[User, Depends(get_current_user)]):
        return {"username": user.username, "role": user.role}

    @app.get("/responsavel-only")
    def responsavel_only(
        user: Annotated[User, Depends(require_role(UserRole.responsavel))]
    ):
        return {"ok": True}

    return app


def test_get_current_user_valid_token(session, test_user):
    app = _make_app(session)
    token = create_access_token({"sub": test_user.username, "role": test_user.role})
    with TestClient(app) as client:
        response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_current_user_invalid_token(session, test_user):
    app = _make_app(session)
    with TestClient(app) as client:
        response = client.get("/me", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401
    assert response.json()["detail"] == "MSG-002"


def test_get_current_user_no_token(session):
    app = _make_app(session)
    with TestClient(app) as client:
        response = client.get("/me")
    assert response.status_code == 401


def test_require_role_authorized(session, test_user):
    """test_user tem role responsavel — deve passar."""
    app = _make_app(session)
    token = create_access_token({"sub": test_user.username, "role": test_user.role})
    with TestClient(app) as client:
        response = client.get(
            "/responsavel-only", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200


def test_require_role_forbidden(session, test_user):
    """Motorista não tem acesso a rota de responsavel."""
    test_user.role = UserRole.motorista
    session.add(test_user)
    session.commit()
    app = _make_app(session)
    token = create_access_token({"sub": test_user.username, "role": UserRole.motorista})
    with TestClient(app) as client:
        response = client.get(
            "/responsavel-only", headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 403
