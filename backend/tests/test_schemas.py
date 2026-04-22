"""Testes de schemas Pydantic."""
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.error import ErrorResponse
from app.schemas.user import UserCreate, UserResponse
from app.models.user import UserRole


def test_login_request_valid():
    req = LoginRequest(username="user", password="pass")
    assert req.username == "user"
    assert req.password == "pass"


def test_token_response_defaults():
    resp = TokenResponse(access_token="tok")
    assert resp.token_type == "bearer"
    assert resp.access_token == "tok"


def test_error_response_defaults():
    err = ErrorResponse(detail="MSG-001", message="Mensagem de erro")
    assert err.fields == []
    assert err.detail == "MSG-001"


def test_error_response_with_fields():
    err = ErrorResponse(detail="MSG-005", message="Campos obrigatórios", fields=["placa", "unidade"])
    assert len(err.fields) == 2


def test_user_create_defaults():
    uc = UserCreate(
        username="joao", full_name="João Silva",
        matricula="123456", password="Senha123"
    )
    assert uc.role == UserRole.motorista


def test_user_response_from_orm(test_user):
    resp = UserResponse.model_validate(test_user)
    assert resp.username == "testuser"
    assert resp.role == UserRole.responsavel
    assert resp.is_active is True
