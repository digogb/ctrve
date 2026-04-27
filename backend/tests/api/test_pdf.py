def test_gerar_pdf_checklist_salvo_200(client, auth_headers, locked_checklist):
    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}/pdf",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f'filename="checklist-{locked_checklist.id}.pdf"' in response.headers["content-disposition"]
    assert response.content[:5] == b"%PDF-"


def test_gerar_pdf_checklist_nao_salvo_400(client, auth_headers, checklist_abc1d23):
    response = client.get(
        f"/api/v1/checklists/{checklist_abc1d23.id}/pdf",
        headers=auth_headers,
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "MSG-019"


def test_gerar_pdf_checklist_inexistente_404(client, auth_headers):
    response = client.get(
        "/api/v1/checklists/99999/pdf",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_gerar_pdf_sem_autenticacao_401(client, locked_checklist):
    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}/pdf",
    )
    assert response.status_code == 401


def test_gerar_pdf_motorista_pode_acessar_200(client, motorista_headers, locked_checklist):
    response = client.get(
        f"/api/v1/checklists/{locked_checklist.id}/pdf",
        headers=motorista_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f'filename="checklist-{locked_checklist.id}.pdf"' in response.headers["content-disposition"]
    assert response.content[:5] == b"%PDF-"


def test_gerar_pdf_checklist_devolvido_200(client, auth_headers, devolvido_locked):
    response = client.get(
        f"/api/v1/checklists/{devolvido_locked.id}/pdf",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert f'filename="checklist-{devolvido_locked.id}.pdf"' in response.headers["content-disposition"]
    assert response.content[:5] == b"%PDF-"
