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


# ── Story 2.2: Busca por Placa (RN-009) ──────────────────────────────────────


def test_search_by_placa_exata(client, test_user, checklist_abc1d23):
    """RN-009: busca pela placa completa retorna o checklist."""
    response = client.get(
        "/api/v1/checklists?placa=ABC1D23",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["placa"] == "ABC1D23"


def test_search_by_placa_parcial(client, test_user, checklist_abc1d23):
    """RN-009: busca por substring retorna checklists com placa contendo o trecho."""
    response = client.get(
        "/api/v1/checklists?placa=ABC",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert any(c["placa"] == "ABC1D23" for c in response.json())


def test_search_case_insensitive(client, test_user, checklist_abc1d23):
    """RN-009: busca é case-insensitive (placa armazenada em maiúsculas)."""
    response = client.get(
        "/api/v1/checklists?placa=abc1d23",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_sem_resultados(client, test_user):
    """RN-009: busca sem correspondência retorna lista vazia (frontend exibe MSG-009)."""
    response = client.get(
        "/api/v1/checklists?placa=ZZZ999",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json() == []


def test_search_sem_filtro(client, test_user, checklist_abc1d23):
    """AC-6: sem parâmetro placa, retorna todos os checklists."""
    response = client.get(
        "/api/v1/checklists",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_search_motorista_pode_buscar(client, motorista_headers, checklist_abc1d23):
    """AC-5: motorista pode buscar — endpoint não exige role responsavel."""
    response = client.get(
        "/api/v1/checklists?placa=ABC1D23",
        headers=motorista_headers,
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_search_ordenado_por_mais_recente(client, test_user, session):
    """AC-2: resultados ordenados por created_at decrescente."""
    from datetime import datetime, timedelta, timezone
    from app.models.checklist import Checklist

    antigo = Checklist(
        placa="XYZ0A00",
        unidade="A",
        motorista="M",
        matricula_motorista="1",
        quilometragem_inicial=1.0,
    )
    antigo.created_at = datetime.now(timezone.utc) - timedelta(hours=1)
    recente = Checklist(
        placa="XYZ0A00",
        unidade="B",
        motorista="N",
        matricula_motorista="2",
        quilometragem_inicial=2.0,
    )
    session.add(antigo)
    session.add(recente)
    session.commit()

    response = client.get(
        "/api/v1/checklists?placa=XYZ0A00",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert results[0]["created_at"] > results[1]["created_at"]  # recente primeiro


# ── Story 3.1: Preencher Checklist de Entrega (RN-010, RN-011, RN-012) ───────


def test_update_entrega_ok(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: PATCH com itens, combustível e data persiste e retorna 200."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nivel_combustivel"] == "3/4"
    assert data["data_entrega"] is not None
    assert len(data["itens"]) == 20
    assert data["itens"][0]["nome"] == "Documento Veicular"
    assert data["itens"][0]["status"] == "ok"


def test_update_entrega_checklist_nao_encontrado(client, test_user, checklist_entrega_payload):
    """404 quando id não existe."""
    response = client.patch(
        "/api/v1/checklists/99999/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 404


def test_update_entrega_locked(client, test_user, session, checklist_entrega_payload):
    """400 quando checklist já está bloqueado."""
    from app.models.checklist import Checklist

    locked = Checklist(
        placa="XYZ1A23",
        unidade="A",
        motorista="M",
        matricula_motorista="1",
        quilometragem_inicial=1.0,
        is_locked=True,
    )
    session.add(locked)
    session.commit()
    session.refresh(locked)

    response = client.patch(
        f"/api/v1/checklists/{locked.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-026"


def test_update_entrega_motorista_proibido(client, motorista_headers, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: motorista não pode fazer PATCH na entrega — requer role responsavel."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=motorista_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "MSG-026"


def test_update_entrega_sem_autenticacao(client, checklist_abc1d23, checklist_entrega_payload):
    """401 quando sem token de autenticação."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
    )
    assert response.status_code == 401


def test_update_entrega_menos_de_20_itens(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """422 quando payload tiver menos de 20 itens."""
    payload_incompleto = {**checklist_entrega_payload, "itens": checklist_entrega_payload["itens"][:5]}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload_incompleto,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_item_status_null(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """422 quando algum item tiver status null."""
    itens_com_null = [
        {"nome": item["nome"], "status": None if i == 0 else item["status"]}
        for i, item in enumerate(checklist_entrega_payload["itens"])
    ]
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json={**checklist_entrega_payload, "itens": itens_com_null},
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_checklist_devolvido(client, test_user, session, checklist_entrega_payload):
    """400 quando checklist já está com status devolvido."""
    from app.models.checklist import Checklist, ChecklistStatus

    devolvido = Checklist(
        placa="DEV0L00",
        unidade="A",
        motorista="M",
        matricula_motorista="1",
        quilometragem_inicial=1.0,
        status=ChecklistStatus.devolvido,
        is_locked=False,
    )
    session.add(devolvido)
    session.commit()
    session.refresh(devolvido)

    response = client.patch(
        f"/api/v1/checklists/{devolvido.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "INVALID_STATUS"


def test_get_one_checklist(client, test_user, checklist_abc1d23):
    """GET /checklists/{id} retorna o checklist correto."""
    response = client.get(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json()["placa"] == "ABC1D23"
    assert response.json()["id"] == checklist_abc1d23.id


def test_get_one_checklist_nao_encontrado(client, test_user):
    """GET /checklists/{id} retorna 404 quando id não existe."""
    response = client.get(
        "/api/v1/checklists/99999",
        headers=_headers(test_user),
    )
    assert response.status_code == 404


# ── Story 3.2: Registrar Avarias no Mapa do Veículo (RN-013, RN-014) ────────


def test_update_entrega_com_avarias(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: PATCH com avarias persiste os pontos de avaria."""
    avarias = [
        {"x": 25.0, "y": 50.0, "vista": "topo", "tipo": "risco"},
        {"x": 75.0, "y": 30.0, "vista": "lateral_esquerda", "tipo": "amassado"},
    ]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["avarias"] is not None
    assert len(data["avarias"]) == 2
    assert data["avarias"][0]["tipo"] == "risco"
    assert data["avarias"][1]["vista"] == "lateral_esquerda"


def test_update_entrega_sem_avarias(client, test_user, checklist_abc1d23, checklist_entrega_payload, session):
    """AC-6: PATCH sem campo avarias não altera avarias existentes."""
    checklist_abc1d23.avarias = [{"x": 10.0, "y": 20.0, "vista": "topo", "tipo": "trincado"}]
    session.add(checklist_abc1d23)
    session.commit()

    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["avarias"] is not None
    assert len(data["avarias"]) == 1
    assert data["avarias"][0]["tipo"] == "trincado"


def test_update_entrega_avaria_sem_tipo(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-3: ponto com tipo inválido retorna 422."""
    avarias = [{"x": 10.0, "y": 20.0, "vista": "topo", "tipo": "inexistente"}]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_avaria_vista_invalida(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: vista fora do enum retorna 422."""
    avarias = [{"x": 10.0, "y": 20.0, "vista": "traseira", "tipo": "risco"}]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_avarias_array_vazio(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-5: array vazio de avarias é aceito (veículo sem avarias é válido)."""
    payload = {**checklist_entrega_payload, "avarias": []}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json()["avarias"] == []


def test_update_entrega_avaria_xy_fora_de_range(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """Coordenadas x/y fora de 0–100 retorna 422."""
    avarias = [{"x": -5.0, "y": 150.0, "vista": "topo", "tipo": "risco"}]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_avaria_tipo_ausente(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """Ponto de avaria sem campo tipo retorna 422."""
    avarias = [{"x": 50.0, "y": 50.0, "vista": "topo"}]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_get_checklist_retorna_avarias(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: GET /{id} retorna avarias no response após PATCH."""
    avarias = [{"x": 50.0, "y": 60.0, "vista": "frontal_traseira", "tipo": "trincado"}]
    payload = {**checklist_entrega_payload, "avarias": avarias}
    client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    response = client.get(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["avarias"] is not None
    assert len(data["avarias"]) == 1
    assert data["avarias"][0]["tipo"] == "trincado"


# ── Story 3.3: Coletar Assinaturas na Entrega (RN-015, RN-016) ──────────────

VALID_SIGNATURE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


def test_update_entrega_com_assinaturas(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: PATCH com assinaturas persiste os campos."""
    payload = {
        **checklist_entrega_payload,
        "assinatura_responsavel": VALID_SIGNATURE,
        "assinatura_motorista": VALID_SIGNATURE,
    }
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel"] == VALID_SIGNATURE
    assert data["assinatura_motorista"] == VALID_SIGNATURE


def test_update_entrega_com_assinatura_atualiza_campo(client, test_user, checklist_abc1d23, checklist_entrega_payload, session):
    """PATCH entrega com assinaturas → persiste ambas as assinaturas."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel"] == VALID_SIGNATURE
    assert data["assinatura_motorista"] == VALID_SIGNATURE


def test_update_entrega_assinatura_formato_invalido(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-4: assinatura sem prefixo data:image/png;base64, retorna 422."""
    payload = {
        **checklist_entrega_payload,
        "assinatura_responsavel": "not-a-valid-base64-string",
    }
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_get_checklist_retorna_assinaturas(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """AC-6: GET /{id} retorna assinaturas no response após PATCH."""
    payload = {
        **checklist_entrega_payload,
        "assinatura_responsavel": VALID_SIGNATURE,
        "assinatura_motorista": VALID_SIGNATURE,
    }
    client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    response = client.get(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel"] == VALID_SIGNATURE
    assert data["assinatura_motorista"] == VALID_SIGNATURE


def test_update_entrega_assinatura_muito_grande(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """Assinatura excedendo max_length retorna 422."""
    oversized = "data:image/png;base64," + "A" * 500_000
    payload = {
        **checklist_entrega_payload,
        "assinatura_responsavel": oversized,
    }
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


# ── Story 4.1: Preencher Checklist de Devolução (RN-017, RN-018, RN-019) ────


def test_update_devolucao_ok(client, test_user, locked_checklist, checklist_devolucao_payload):
    """PATCH com payload válido em checklist locked+entregue → 200 + status devolvido."""
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "devolvido"
    assert data["quilometragem_final"] == 51000.0
    assert data["nivel_combustivel_devolucao"] == "2/4"
    assert data["data_devolucao"] is not None
    assert len(data["itens_devolucao"]) == 20


def test_update_devolucao_sem_entrega_previa(client, test_user, checklist_abc1d23, checklist_devolucao_payload):
    """PATCH em checklist não locked → 400 MSG-015."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-015"


def test_update_devolucao_quilometragem_menor(client, test_user, locked_checklist, checklist_devolucao_payload):
    """quilometragem_final < quilometragem_inicial → 400 MSG-016."""
    payload = {**checklist_devolucao_payload, "quilometragem_final": 1000.0}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-016"
    assert "quilometragem_final" in response.json()["fields"]


def test_update_devolucao_data_anterior(client, test_user, locked_checklist, checklist_devolucao_payload):
    """data_devolucao < data_entrega → 400 MSG-017."""
    payload = {**checklist_devolucao_payload, "data_devolucao": "2026-04-19T08:00:00Z"}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-017"
    assert "data_devolucao" in response.json()["fields"]


def test_update_devolucao_itens_incompletos(client, test_user, locked_checklist, checklist_devolucao_payload):
    """Menos de 20 itens → 422."""
    payload = {**checklist_devolucao_payload, "itens": checklist_devolucao_payload["itens"][:5]}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_devolucao_motorista_proibido(client, motorista_headers, locked_checklist, checklist_devolucao_payload):
    """Motorista tenta PATCH → 403 MSG-026."""
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=motorista_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "MSG-026"


def test_get_checklist_retorna_campos_devolucao(client, test_user, locked_checklist, checklist_devolucao_payload):
    """GET /{id} retorna todos os campos de devolução após PATCH."""
    client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "devolvido"
    assert data["quilometragem_final"] == 51000.0
    assert data["nivel_combustivel_devolucao"] == "2/4"
    assert data["itens_devolucao"] is not None
    assert len(data["itens_devolucao"]) == 20


def test_update_devolucao_checklist_nao_encontrado(client, test_user, checklist_devolucao_payload):
    """404 quando checklist não existe."""
    response = client.patch(
        "/api/v1/checklists/99999/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 404


def test_update_devolucao_quilometragem_igual(client, test_user, locked_checklist, checklist_devolucao_payload):
    """Boundary: quilometragem_final == quilometragem_inicial (50000) deve ser aceito."""
    payload = {**checklist_devolucao_payload, "quilometragem_final": 50000.0}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json()["quilometragem_final"] == 50000.0


def test_update_devolucao_data_igual_entrega(client, test_user, locked_checklist, checklist_devolucao_payload):
    """Boundary: data_devolucao == data_entrega deve ser aceito."""
    payload = {**checklist_devolucao_payload, "data_devolucao": "2026-04-20T10:00:00Z"}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200


def test_update_devolucao_is_locked_permanece_true(client, test_user, locked_checklist, checklist_devolucao_payload):
    """is_locked permanece True após devolução (lock gerenciado pela Story 5.1)."""
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json()["is_locked"] is True


def test_update_devolucao_em_checklist_devolvido(client, test_user, session, checklist_devolucao_payload):
    """Devolução em checklist já devolvido → 400 MSG-015."""
    from app.models.checklist import Checklist, ChecklistStatus

    devolvido = Checklist(
        placa="DEV0L00",
        unidade="A",
        motorista="M",
        matricula_motorista="1",
        quilometragem_inicial=1.0,
        status=ChecklistStatus.devolvido,
        is_locked=True,
    )
    session.add(devolvido)
    session.commit()
    session.refresh(devolvido)

    response = client.patch(
        f"/api/v1/checklists/{devolvido.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-015"


# ── Story 4.2: Assinaturas na Devolução ────────────────────────────────────


def test_update_devolucao_com_assinaturas(client, test_user, locked_checklist, checklist_devolucao_payload):
    """PATCH com assinaturas válidas → 200 + campos persistidos."""
    payload = {
        **checklist_devolucao_payload,
        "assinatura_responsavel": VALID_SIGNATURE,
        "assinatura_motorista": VALID_SIGNATURE,
    }
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel_devolucao"] == VALID_SIGNATURE
    assert data["assinatura_motorista_devolucao"] == VALID_SIGNATURE


def test_update_devolucao_assinatura_formato_invalido(client, test_user, locked_checklist, checklist_devolucao_payload):
    """Assinatura sem prefixo data:image/png;base64, → 422."""
    payload = {
        **checklist_devolucao_payload,
        "assinatura_responsavel": "not-a-valid-base64-string",
    }
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_get_checklist_retorna_assinaturas_devolucao(client, test_user, locked_checklist, checklist_devolucao_payload):
    """GET /{id} retorna assinaturas de devolução após PATCH."""
    payload = {
        **checklist_devolucao_payload,
        "assinatura_responsavel": VALID_SIGNATURE,
        "assinatura_motorista": VALID_SIGNATURE,
    }
    patch_resp = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert patch_resp.status_code == 200
    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel_devolucao"] == VALID_SIGNATURE
    assert data["assinatura_motorista_devolucao"] == VALID_SIGNATURE


def test_update_devolucao_com_assinatura_atualiza_campo(client, test_user, locked_checklist, checklist_devolucao_payload, session):
    """PATCH devolução com assinaturas → persiste ambas as assinaturas."""
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=checklist_devolucao_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assinatura_responsavel_devolucao"] == VALID_SIGNATURE
    assert data["assinatura_motorista_devolucao"] == VALID_SIGNATURE


# ── Story 4.3: Registrar Observações (RN-020) ────────────────────────────────


def test_update_entrega_com_observacoes(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """PATCH entrega com observacoes persiste o campo."""
    payload = {**checklist_entrega_payload, "observacoes": "Veículo com arranhão na porta traseira"}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["observacoes"] == "Veículo com arranhão na porta traseira"


def test_update_entrega_sem_observacoes_nao_altera(client, test_user, checklist_abc1d23, checklist_entrega_payload, session):
    """PATCH entrega sem campo observacoes não altera observacoes existentes."""
    checklist_abc1d23.observacoes = "Observação pré-existente"
    session.add(checklist_abc1d23)
    session.commit()

    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["observacoes"] == "Observação pré-existente"


def test_update_devolucao_com_observacoes(client, test_user, locked_checklist, checklist_devolucao_payload):
    """PATCH devolução com observacoes persiste em observacoes_devolucao."""
    payload = {**checklist_devolucao_payload, "observacoes": "Pneu dianteiro desgastado"}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["observacoes_devolucao"] == "Pneu dianteiro desgastado"


def test_get_checklist_retorna_observacoes(client, test_user, locked_checklist, checklist_devolucao_payload):
    """GET /{id} retorna observacoes e observacoes_devolucao."""
    payload = {**checklist_devolucao_payload, "observacoes": "Obs devolução"}
    patch_resp = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert patch_resp.status_code == 200

    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}",
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert "observacoes" in data
    assert "observacoes_devolucao" in data
    assert data["observacoes_devolucao"] == "Obs devolução"


def test_observacoes_campo_vazio_aceito(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """PATCH com observacoes vazio é aceito (campo opcional)."""
    payload = {**checklist_entrega_payload, "observacoes": ""}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["observacoes"] == ""


# ── Story 5.1: Salvar Checklist (RN-015, RN-016) ────────────────────────────


def test_update_entrega_bloqueia_checklist(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """T5.1 — PATCH entrega com payload completo (inclui assinaturas) → 200 + is_locked True."""
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 200
    assert response.json()["is_locked"] is True


def test_update_entrega_locked_rejeita_update(client, test_user, session, checklist_entrega_payload):
    """T5.2 — PATCH entrega em checklist já locked → 400 MSG-026."""
    from app.models.checklist import Checklist

    locked = Checklist(
        placa="LCK0A00",
        unidade="A",
        motorista="M",
        matricula_motorista="1",
        quilometragem_inicial=1.0,
        is_locked=True,
    )
    session.add(locked)
    session.commit()
    session.refresh(locked)

    response = client.patch(
        f"/api/v1/checklists/{locked.id}/entrega",
        json=checklist_entrega_payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "MSG-026"


def test_update_entrega_sem_assinatura_responsavel_422(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """T5.3 — PATCH entrega sem assinatura_responsavel → 422 MSG-014."""
    payload = {**checklist_entrega_payload, "assinatura_responsavel": None}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_entrega_sem_assinatura_motorista_422(client, test_user, checklist_abc1d23, checklist_entrega_payload):
    """T5.4 — PATCH entrega sem assinatura_motorista → 422 MSG-014."""
    payload = {**checklist_entrega_payload, "assinatura_motorista": None}
    response = client.patch(
        f"/api/v1/checklists/{checklist_abc1d23.id}/entrega",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_devolucao_sem_assinatura_responsavel_422(client, test_user, locked_checklist, checklist_devolucao_payload):
    """T5.5 — PATCH devolução sem assinatura_responsavel → 422 MSG-014."""
    payload = {**checklist_devolucao_payload, "assinatura_responsavel": None}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_update_devolucao_sem_assinatura_motorista_422(client, test_user, locked_checklist, checklist_devolucao_payload):
    """T5.6 — PATCH devolução sem assinatura_motorista → 422 MSG-014."""
    payload = {**checklist_devolucao_payload, "assinatura_motorista": None}
    response = client.patch(
        f"/api/v1/checklists/{locked_checklist.id}/devolucao",
        json=payload,
        headers=_headers(test_user),
    )
    assert response.status_code == 422


def test_cancelar_checklist_nao_salvo_204(client, auth_headers, checklist_abc1d23):
    response = client.delete(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204
    get_response = client.get(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_cancelar_checklist_salvo_400(client, auth_headers, locked_checklist):
    response = client.delete(
        f"/api/v1/checklists/{locked_checklist.id}",
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "LOCKED"


def test_cancelar_checklist_inexistente_404(client, auth_headers):
    response = client.delete("/api/v1/checklists/99999", headers=auth_headers)
    assert response.status_code == 404


def test_cancelar_checklist_sem_auth_401(client, checklist_abc1d23):
    response = client.delete(f"/api/v1/checklists/{checklist_abc1d23.id}")
    assert response.status_code == 401


def test_cancelar_checklist_motorista_403(client, motorista_headers, checklist_abc1d23):
    response = client.delete(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=motorista_headers,
    )
    assert response.status_code == 403
