# Story 5.3: Cancelar Checklist

Status: done

## Story

Como Responsável,
quero cancelar o preenchimento de um checklist antes de salvá-lo,
para que eu possa descartar um checklist iniciado por engano sem que dados incorretos sejam persistidos.

## Acceptance Criteria

1. Botão "Cancelar" disponível no formulário de entrega enquanto `checklist.is_locked === false` (estado `isFillingEntrega`).
2. Ao clicar, sistema exibe MSG-020 via `window.confirm()`: "Deseja cancelar o preenchimento? Todos os dados informados serão descartados."
3. Após confirmação, checklist é deletado via `DELETE /api/v1/checklists/{id}` e usuário é redirecionado para `/` (tela principal).
4. Se cancelamento negado (`window.confirm` retorna `false`), formulário é mantido com todos os dados preservados — nenhuma chamada à API, sem rerender.
5. Botão "Cancelar" não aparece quando checklist está salvo (`is_locked === true`).
6. Endpoint `DELETE /api/v1/checklists/{id}` retorna 204 No Content. Requer autenticação com perfil `responsavel`.
7. Tentativa de deletar checklist já salvo (`is_locked === true`) retorna 400 com `detail: "LOCKED"`.
8. Botão "Cancelar" também presente em `ChecklistForm.tsx` (antes de criar o checklist) — clique navega diretamente para `/` sem confirmação (nenhum dado foi persistido no banco ainda).
9. Testes backend: 204 sucesso, 400 locked, 404 not found, 401 sem auth, 403 motorista. Testes frontend: botão visível/oculto conforme lock state, confirmação → DELETE chamado, negação → DELETE não chamado.

## Tasks / Subtasks

- [x] **T1 — Backend: função cancel_checklist (AC: 6, 7)**
  - [x] T1.1: Em `backend/app/services/checklist_service.py`, adicionar `cancel_checklist(session: Session, checklist_id: int) -> None` **após** a função `get_checklist_by_id`
  - [x] T1.2: Reutilizar `get_checklist_by_id()` para buscar e garantir 404 se não encontrado
  - [x] T1.3: Guard: se `checklist.is_locked`, raise `ChecklistError(400, "LOCKED", "Checklist bloqueado não pode ser cancelado.", [])`
  - [x] T1.4: `session.delete(checklist)` + `session.commit()`

- [x] **T2 — Backend: endpoint DELETE (AC: 6, 7)**
  - [x] T2.1: Em `backend/app/api/routes/checklists.py`, adicionar `cancel_checklist` ao import de `checklist_service`
  - [x] T2.2: Adicionar `Response` ao import de `fastapi`
  - [x] T2.3: Adicionar `@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)` com `require_role(UserRole.responsavel)`
  - [x] T2.4: Retornar `Response(status_code=status.HTTP_204_NO_CONTENT)` — FastAPI exige Response explícito para 204 (sem body)

- [x] **T3 — Backend: testes (AC: 6, 7, 9)**
  - [x] T3.1: `test_cancelar_checklist_nao_salvo_204`: DELETE `checklist_abc1d23` → 204, GET posterior → 404 (confirmar deleção)
  - [x] T3.2: `test_cancelar_checklist_salvo_400`: DELETE `locked_checklist` → 400, `data["detail"] == "LOCKED"`
  - [x] T3.3: `test_cancelar_checklist_inexistente_404`: DELETE `/checklists/99999` → 404
  - [x] T3.4: `test_cancelar_checklist_sem_auth_401`: DELETE sem header → 401
  - [x] T3.5: `test_cancelar_checklist_motorista_403`: DELETE com `motorista_headers` → 403

- [x] **T4 — Frontend: botão Cancelar no ChecklistView (AC: 1-5, 9)**
  - [x] T4.1: Em `ChecklistView.tsx`, adicionar `useNavigate` ao import de `react-router-dom` (linha 2)
  - [x] T4.2: Adicionar `const navigate = useNavigate()` junto com os outros hooks no componente `ChecklistView`
  - [x] T4.3: Implementar `onCancel` com window.confirm + apiClient.delete + navigate("/")
  - [x] T4.4: No bloco `{isFillingEntrega && ...}`, flex container com Salvar + Cancelar

- [x] **T5 — Frontend: botão Cancelar no ChecklistForm (AC: 8)**
  - [x] T5.1: Em `ChecklistForm.tsx`, adicionar botão abaixo do botão "Criar Checklist" (dentro do `<form>`)
  - [x] T5.2: `<Button type="button" variant="outline" className="mt-2 w-full" onClick={() => navigate("/")} disabled={isSubmitting}>Cancelar</Button>`
  - [x] T5.3: `useNavigate` e `navigate` já existem em `ChecklistForm.tsx` — nenhum import adicional necessário

- [x] **T6 — Frontend: testes (AC: 1-5, 9)**
  - [x] T6.1: Adicionar `delete: vi.fn()` ao mock do `apiClient` no topo de `ChecklistView.test.tsx`
  - [x] T6.2: `test_cancelar_botao_visivel_quando_nao_locked`: Botão "Cancelar" visível quando `is_locked: false`
  - [x] T6.3: `test_cancelar_botao_invisivel_quando_locked`: Botão "Cancelar" não no DOM quando `is_locked: true`
  - [x] T6.4: `test_cancelar_com_confirmacao_chama_delete`: `window.confirm` → `true`, botão clicado → `apiClient.delete` chamado com `/v1/checklists/1`
  - [x] T6.5: `test_cancelar_com_negacao_nao_chama_delete`: `window.confirm` → `false`, botão clicado → `apiClient.delete` **não** chamado, botão permanece no DOM

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `get_checklist_by_id()` | `checklist_service.py:24-34` | Pronto — reutilizar para busca + 404 automático |
| `ChecklistError` + handler | `checklist_service.py:11-23`, `main.py:68-73` | Pronto — reutilizar para guard locked |
| `require_role(UserRole.responsavel)` | `core/deps.py` | Pronto — usar no DELETE endpoint |
| `auth_headers` / `motorista_headers` fixtures | `conftest.py:78-197` | Pronto — reutilizar nos testes |
| `checklist_abc1d23` fixture (`is_locked=False`) | `conftest.py:88-103` | Pronto — usar no teste de DELETE 204 |
| `locked_checklist` fixture (`is_locked=True`) | `conftest.py:118-137` | Pronto — usar no teste de DELETE 400 |
| `apiClient` (axios instance com `.delete`) | `lib/apiClient.ts` | Pronto — `.delete` é método nativo do axios |
| `isAxiosError` export | `lib/apiClient.ts:17` | Pronto |
| `Button` component (shadcn) | `components/ui/button.tsx` | Pronto |
| `useNavigate` + `navigate` | `ChecklistForm.tsx:3,7` | **Já existe** em ChecklistForm — só adicionar em ChecklistView |
| `Response` do fastapi | Já importado em `routes/pdf.py` | Adicionar ao import de `checklists.py` |

### O que falta (escopo desta story)

1. Função `cancel_checklist()` em `checklist_service.py`
2. Endpoint `DELETE /checklists/{id}` em `checklists.py` (4 linhas)
3. 5 testes em `backend/tests/api/test_checklists.py` — **arquivo já existe**, adicionar ao final
4. Botão "Cancelar" + `onCancel` + `useNavigate` em `ChecklistView.tsx`
5. Botão "Cancelar" em `ChecklistForm.tsx` (3 linhas)
6. 4 testes em `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx` — **arquivo já existe**

**Nenhum arquivo novo.** Todos os arquivos já existem.

### Padrão de referência — cancel_checklist em checklist_service.py

```python
def cancel_checklist(session: Session, checklist_id: int) -> None:
    checklist = get_checklist_by_id(session, checklist_id)
    if checklist.is_locked:
        raise ChecklistError(
            status_code=400,
            detail="LOCKED",
            message="Checklist bloqueado não pode ser cancelado.",
            fields=[],
        )
    session.delete(checklist)
    session.commit()
```

### Padrão de referência — DELETE endpoint em checklists.py

```python
# Adicionar ao import existente:
from fastapi import APIRouter, Depends, Response, status

# Adicionar ao import de checklist_service:
from app.services.checklist_service import (
    cancel_checklist,
    create_checklist,
    ...
)

@router.delete("/{checklist_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel(
    checklist_id: int,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    cancel_checklist(session, checklist_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

**IMPORTANTE**: `return Response(status_code=204)` é obrigatório. Se retornar `None` (implícito), FastAPI tentará serializar como JSON e pode gerar erro de encoding com body vazio.

### Padrão de referência — Testes backend

Adicionar ao final de `backend/tests/api/test_checklists.py`:

```python
def test_cancelar_checklist_nao_salvo_204(client, auth_headers, checklist_abc1d23):
    response = client.delete(
        f"/api/v1/checklists/{checklist_abc1d23.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204
    # Confirmar deleção
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
```

### Padrão de referência — Testes frontend

**Passo 1:** Adicionar `delete: vi.fn()` ao mock do apiClient (bloco `vi.mock` no topo do arquivo):

```typescript
vi.mock("../../../lib/apiClient", () => ({
  default: {
    get: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),          // ← ADICIONAR ESTA LINHA
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
  setAccessToken: vi.fn(),
  clearAccessToken: vi.fn(),
  getAccessToken: vi.fn(),
  isAxiosError: vi.fn(() => false),
}));
```

**Passo 2:** Adicionar os 4 testes ao `describe("ChecklistView")`:

```typescript
it("exibe botão Cancelar quando checklist não está salvo", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST }); // is_locked: false
  renderAt("1");
  await waitFor(() => {
    expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
  });
});

it("não exibe botão Cancelar quando checklist está salvo", async () => {
  const locked = { ...BASE_CHECKLIST, is_locked: true };
  vi.mocked(apiClient.get).mockResolvedValue({ data: locked });
  renderAt("1");
  await waitFor(() => {
    // Tela read-only é exibida
    expect(screen.getByText(/checklist de entrega/i)).toBeInTheDocument();
  });
  expect(screen.queryByRole("button", { name: /cancelar/i })).not.toBeInTheDocument();
});

it("clique em Cancelar com confirmação chama DELETE", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
  vi.mocked(apiClient.delete).mockResolvedValue({});
  vi.spyOn(window, "confirm").mockReturnValueOnce(true);

  renderAt("1");
  await waitFor(() => screen.getByRole("button", { name: /cancelar/i }));
  fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));

  await waitFor(() => {
    expect(apiClient.delete).toHaveBeenCalledWith("/v1/checklists/1");
  });
});

it("clique em Cancelar com negação não chama DELETE", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
  vi.mocked(apiClient.delete).mockResolvedValue({});
  vi.spyOn(window, "confirm").mockReturnValueOnce(false);

  renderAt("1");
  await waitFor(() => screen.getByRole("button", { name: /cancelar/i }));
  fireEvent.click(screen.getByRole("button", { name: /cancelar/i }));

  expect(apiClient.delete).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: /cancelar/i })).toBeInTheDocument();
});
```

**NOTA sobre `window.confirm` no Vitest**: `vi.spyOn(window, "confirm").mockReturnValueOnce(true)` substitui o `confirm` para uma chamada. Usar `mockReturnValueOnce` para garantir que não vaza entre testes. O spy não precisa ser restaurado manualmente pois `vi.clearAllMocks()` no `beforeEach` já cobre isso.

### Banco de dados

Sem alteração no modelo. Sem migração. Não deletar `ctrve.db`.

### Impacto em testes existentes

Nenhum. A adição de `delete: vi.fn()` ao mock é retrocompatível — testes existentes que não usam `apiClient.delete` não são afetados. O endpoint DELETE é novo e não interfere com endpoints existentes. O botão "Cancelar" é adicionado ao JSX sem alterar lógica existente.

### Anti-padrões (PROIBIDO)

- `navigate(-1)` — deve ser `navigate("/")` (tela principal Dashboard, rota `/`)
- Deletar o checklist sem confirmação MSG-020
- Endpoint POST ou PATCH para cancelar — usar DELETE (semântica REST correta)
- Retornar 200 com body no DELETE — deve ser `Response(status_code=204)` sem body
- `window.alert` para MSG-020 — deve ser `window.confirm` (mensagem de confirmação)
- Criar `ConfirmDialog.tsx` — fora do escopo desta story; `window.confirm` é o padrão estabelecido na codebase (ver MSG-018 em `ChecklistView.tsx:201,360`)
- Redirecionar para `/checklists` — redirecionar para `/` (Dashboard = tela principal)

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 5.3 |
|-------------|--------------|-----------------|
| `ChecklistError(400, detail, message, [])` para guards de negócio | Todas as stories | Guard `is_locked` no DELETE |
| `require_role(UserRole.responsavel)` em endpoints de escrita | `checklists.py:42,60` | DELETE exige responsavel |
| `window.confirm(MSG-018)` padrão de confirmação | `ChecklistView.tsx:201,360` | MSG-020 segue mesmo padrão |
| `navigate("/")` para home | `ChecklistForm.tsx` não usa ainda, mas `routes.tsx` confirma rota `/` = Dashboard | Cancel navega para "/" |
| `Response(status_code=204)` explícito | `routes/pdf.py` usa Response | DELETE retorna 204 sem body |
| `vi.mocked(apiClient.get).mockResolvedValue(...)` | `ChecklistView.test.tsx` | Mesmo padrão para `apiClient.delete` |
| `vi.spyOn(window, "confirm")` em Vitest | Padrão Vitest | Mockar `window.confirm` nos testes |
| `checklist_abc1d23` fixture tem `is_locked=False` | `conftest.py:88-103` | Fixture certa para testar cancel 204 |
| FastAPI 204: `return Response(status_code=204)` é obrigatório | Padrão FastAPI descoberto em story 5.2 | Aplicar no DELETE |

### Sequência de Implementação Recomendada

1. T1 (service) → verificar com `python -c "from app.services.checklist_service import cancel_checklist"`
2. T2 (endpoint DELETE) → testar com `curl -X DELETE http://localhost:8000/api/v1/checklists/1 -H "Authorization: Bearer ..."` ou TestClient
3. T3 (testes backend) → `pytest backend/tests/api/test_checklists.py -k "cancelar" -v`
4. T4 (ChecklistView — Cancelar) → testar manualmente no browser
5. T5 (ChecklistForm — Cancelar) → testar manualmente no browser
6. T6 (testes frontend) → `npm test -- ChecklistView`

### Project Structure Notes

**Arquivos modificados nesta story (nenhum arquivo novo):**

| Arquivo | Tipo de mudança |
|---------|-----------------|
| `backend/app/services/checklist_service.py` | Adicionar `cancel_checklist()` |
| `backend/app/api/routes/checklists.py` | Adicionar DELETE endpoint + imports |
| `backend/tests/api/test_checklists.py` | Adicionar 5 testes ao final |
| `frontend/src/features/checklist/ChecklistView.tsx` | Adicionar `useNavigate`, `onCancel`, botão Cancelar |
| `frontend/src/features/checklist/ChecklistForm.tsx` | Adicionar botão Cancelar (3 linhas) |
| `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx` | Adicionar `delete: vi.fn()` ao mock + 4 testes |

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-024
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-020
- User story: `_bmad-output/requirements/user-stories.md` — US-013
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — US-013 → ChecklistForm.tsx + ConfirmDialog.tsx (ConfirmDialog postergado — window.confirm é o padrão atual)
- Epics: `_bmad-output/planning-artifacts/epics.md` — Story 5.3
- Story anterior: `_bmad-output/implementation-artifacts/5-2-gerar-e-compartilhar-pdf.md` — padrões apiClient, window.alert/confirm, Button
- Deferred work: `_bmad-output/implementation-artifacts/deferred-work.md` — nenhum item diretamente aplicável a esta story

## Review Findings

#### Decision Needed

- [x] [Review][Decision] `onCancel` navega para `/` mesmo quando DELETE retorna 4xx — **decisão: exibir erro ao usuário em 4xx (ex: 400 LOCKED); apenas erros de rede navegam silenciosamente para home**. [frontend/src/features/checklist/ChecklistView.tsx]

#### Patches

- [x] [Review][Patch] `onCancel` — exibe `window.alert` com erro em 4xx; apenas erros de rede navegam silenciosamente para home. [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Botão Cancelar — `isCancelling` state adicionado; botão disabled e texto "Cancelando..." durante o DELETE. [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Testes para botão Cancelar em `ChecklistForm.tsx` — cobertura AC-8 adicionada (presença + navegação sem `window.confirm`). [frontend/src/features/checklist/__tests__/ChecklistForm.test.tsx]

#### Deferred

- [x] [Review][Defer] Hard delete sem audit trail — sem campos `cancelled_at`/`cancelled_by`; adequado para MVP, mas pode ter implicações regulatórias/rastreabilidade. [backend/app/services/checklist_service.py] — deferred
- [x] [Review][Defer] `session.commit()` dentro da camada de serviço — padrão pré-existente na codebase; tratar em refactor de unit-of-work. [backend/app/services/checklist_service.py] — deferred, pre-existing
- [x] [Review][Defer] `checklist_abc1d23` nome opaco de fixture — padrão pré-existente em toda a suite de testes; renomear para `unlocked_checklist` em refactor cross-story. — deferred, pre-existing
- [x] [Review][Defer] Sem isolamento de ownership no DELETE — qualquer `responsavel` pode deletar qualquer checklist; decisão arquitetural pré-existente de multi-tenant. [backend/app/api/routes/checklists.py] — deferred, pre-existing
- [x] [Review][Defer] Sem unit test para `cancel_checklist` isolado da camada HTTP — padrão pré-existente de integration tests via TestClient. [backend/tests/api/test_checklists.py] — deferred, pre-existing

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 — 2026-04-27

### Completion Notes

- Backend: `cancel_checklist()` adicionado em `checklist_service.py` após `get_checklist_by_id`. Reusa o helper existente para 404; guard de `is_locked` retorna 400 `detail="LOCKED"`; deleta e commita.
- Backend: `DELETE /api/v1/checklists/{id}` em `checklists.py` — `require_role(responsavel)`, `Response(status_code=204)` explícito.
- Backend: 5 testes novos em `test_checklists.py` — 204+GET 404, 400 locked, 404 not found, 401, 403. Todos passando. Total: 106 testes (sem regressões).
- Frontend: `useNavigate` + `onCancel` adicionados em `ChecklistView.tsx`. Botão Cancelar ao lado do Salvar no formulário de entrega.
- Frontend: Botão Cancelar adicionado em `ChecklistForm.tsx` (navega para "/" sem confirmação — nenhum dado em DB ainda).
- Frontend: `delete: vi.fn()` adicionado ao mock; 4 testes novos passando. Total: 100 testes (sem regressões).

### Change Log

- 2026-04-27: Story 5.3 implementada — `cancel_checklist()` + `DELETE /checklists/{id}` + 5 testes backend + botão Cancelar em ChecklistView/ChecklistForm + 4 testes frontend.

## File List

- backend/app/services/checklist_service.py (modificado)
- backend/app/api/routes/checklists.py (modificado)
- backend/tests/api/test_checklists.py (modificado)
- frontend/src/features/checklist/ChecklistView.tsx (modificado)
- frontend/src/features/checklist/ChecklistForm.tsx (modificado)
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx (modificado)
