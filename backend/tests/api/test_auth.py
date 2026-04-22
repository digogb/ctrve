def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Senha123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "refresh_token" in response.cookies


def test_login_invalid_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "MSG-001"


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "naoexiste", "password": "qualquer"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "MSG-001"


def test_login_same_error_for_invalid_and_unknown(client, test_user):
    """RN-001: mesma mensagem para usuário/senha inválidos (sem revelar qual)."""
    r1 = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "errada"},
    )
    r2 = client.post(
        "/api/v1/auth/login",
        json={"username": "naoexiste", "password": "qualquer"},
    )
    assert r1.json()["detail"] == r2.json()["detail"] == "MSG-001"


def test_refresh_success(client, test_user):
    login = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "Senha123"},
    )
    assert login.status_code == 200

    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_refresh_without_cookie(client):
    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 401
    assert response.json()["detail"] == "MSG-002"
