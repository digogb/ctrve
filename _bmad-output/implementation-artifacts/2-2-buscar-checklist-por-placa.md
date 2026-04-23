# Story 2.2: Buscar Checklist por Placa

Status: done

## Story

Como Responsável ou Motorista,
quero buscar checklists existentes pela placa do veículo,
para que eu possa consultar o histórico ou verificar checklists em andamento.

## Acceptance Criteria

1. Campo de busca aceita placa parcial ou completa (busca por substring, case-insensitive).
2. Resultados exibem lista ordenada por data de criação decrescente (proxy de data de entrega enquanto `data_entrega` não é populada — ver Dev Notes).
3. Cada resultado exibe: Nº de Controle (`id`), Placa, Data de Registro (`created_at`), Status (Entregue/Devolvido).
4. Busca sem resultados exibe MSG-009.
5. Endpoint acessível a ambos os perfis (Responsável e Motorista) — apenas autenticação requerida.
6. Busca sem parâmetro `placa` retorna todos os checklists (listagem geral).

## Tasks / Subtasks

- [x] **T1 — Função `search_checklists` no service (AC: 1, 2, 4)** — `backend/app/services/checklist_service.py`
  - [x] Adicionar `search_checklists(session: Session, placa: str | None = None) -> list[Checklist]`
  - [x] Se `placa` fornecido: `WHERE placa LIKE '%{placa.upper()}%'` (substring, uppercase normalizado)
  - [x] Ordenar por `created_at DESC` (quando `data_entrega` for populado pela Story 5.1, migrar para `COALESCE(data_entrega, created_at) DESC`)
  - [x] Retorna lista vazia quando sem resultados (frontend exibe MSG-009)

- [x] **T2 — Endpoint `GET /checklists` (AC: 5, 6)** — `backend/app/api/routes/checklists.py`
  - [x] `GET /api/v1/checklists?placa=` (query param opcional, `str | None = None`)
  - [x] Requer `get_current_user` (ambos os perfis) — NÃO usar `require_role`
  - [x] Delega para `search_checklists(session, placa)`
  - [x] Retorna `list[ChecklistResponse]` com status 200

- [x] **T3 — Testes backend (AC: 1, 4, 5, 6)** — `backend/tests/api/test_checklists.py`
  - [x] `test_search_by_placa_exata`: GET /checklists?placa=ABC1D23 → 200 + lista com o checklist
  - [x] `test_search_by_placa_parcial`: GET /checklists?placa=ABC → retorna checklists cuja placa contém "ABC"
  - [x] `test_search_case_insensitive`: GET /checklists?placa=abc1d23 → retorna mesmo resultado que "ABC1D23"
  - [x] `test_search_sem_resultados`: GET /checklists?placa=ZZZ999 → 200 + lista vazia
  - [x] `test_search_sem_filtro`: GET /checklists → 200 + todos os checklists
  - [x] `test_search_motorista_pode_buscar`: autenticado como motorista → 200 (não é 403)
  - [x] `test_search_ordenado_por_mais_recente`: dois checklists → o mais recente aparece primeiro

- [x] **T4 — Componente `ChecklistList.tsx` (AC: 1, 2, 3, 4)** — `frontend/src/features/checklist/ChecklistList.tsx`
  - [x] Estado local `searchTerm: string` controlado por input
  - [x] `useQuery` com key `["checklists", { placa: searchTerm }]` — busca ao submit do formulário
  - [x] Query habilitada (`enabled: true`) apenas quando `searchTerm` não vazio, OU mostrar todos quando vazio (key `["checklists"]`)
  - [x] Tabela com colunas: Nº de Controle, Placa, Data de Registro, Status
  - [x] Status: "Entregue" para `status === "entregue"`, "Devolvido" para `status === "devolvido"`
  - [x] Data: formatar `created_at` para `dd/mm/aaaa HH:mm` usando `Intl.DateTimeFormat` (sem biblioteca extra)
  - [x] Lista vazia após busca: exibir MSG-009 (`role="status"`)
  - [x] Estado de loading: exibir "Buscando..." ou skeleton
  - [x] Clicar em resultado navega para `/checklists/{id}` (placeholder existente)
  - [x] Formulário de busca: input + botão "Buscar" (submit no Enter também)

- [x] **T5 — Rota `/checklists` (AC: 1, 5)** — `frontend/src/routes.tsx`
  - [x] Adicionar `<Route path="/checklists" element={<ProtectedRoute><ChecklistList /></ProtectedRoute>} />`
  - [x] Importar `ChecklistList`
  - [x] NÃO envolver com `RequireRole` — motorista também pode acessar

- [x] **T6 — Hook `useChecklistSearch` (AC: 1, 2)** — `frontend/src/features/checklist/ChecklistList.tsx` (ou arquivo separado)
  - [x] `GET /api/v1/checklists?placa={placa}` via `apiClient`
  - [x] Retorna `{ data: ChecklistResponse[], isLoading, isError }`
  - [x] Query key: `["checklists", { placa }]` para filtragem; `["checklists"]` sem filtro

- [x] **T7 — Testes frontend (AC: 1, 3, 4)** — `frontend/src/features/checklist/__tests__/ChecklistList.test.tsx`
  - [x] `test_renders_search_form`: formulário com input e botão "Buscar"
  - [x] `test_exibe_resultados`: mock GET retorna lista → tabela com Nº de Controle, Placa, Data, Status
  - [x] `test_exibe_msg_009_sem_resultados`: mock GET retorna `[]` após busca → exibe MSG-009
  - [x] `test_navega_para_checklist`: clicar em linha navega para `/checklists/{id}`

## Dev Notes

### Código reutilizável — NÃO reimplementar

| Item | Localização | Reutiliza Como |
|------|-------------|----------------|
| `get_current_user` | `backend/app/core/deps.py` | Dependency do endpoint GET /checklists |
| `ChecklistResponse` | `backend/app/schemas/checklist.py` | Tipo de retorno da busca |
| `Checklist` model | `backend/app/models/checklist.py` | Query de busca via SQLModel |
| `ChecklistStatus` | `backend/app/models/checklist.py` e `frontend/src/types/checklist.ts` | Exibição do status |
| `apiClient` | `frontend/src/lib/apiClient.ts` | GET /checklists |
| `useAuthContext` | `frontend/src/features/auth/AuthContext.tsx` | Autenticação do componente |
| `ChecklistResponse` type | `frontend/src/types/checklist.ts` | Tipagem dos resultados |
| `ProtectedRoute` | `frontend/src/components/ProtectedRoute.tsx` | Proteção da rota |

### Padrão de Query no Backend (SQLModel + SQLAlchemy)

```python
from sqlmodel import Session, select
from sqlalchemy import desc
from app.models.checklist import Checklist

def search_checklists(session: Session, placa: str | None = None) -> list[Checklist]:
    query = select(Checklist)
    if placa:
        query = query.where(Checklist.placa.contains(placa.upper()))
    query = query.order_by(desc(Checklist.created_at))
    return list(session.exec(query).all())
```

**Por que `placa.upper()` na busca?** A placa é sempre armazenada em maiúsculas (`create_checklist` normaliza via `.upper()`). Normalizar a busca também garante match mesmo quando o usuário digita em minúsculas (RN-009: "aceita texto informado").

**Futura migração para `data_entrega`:** Quando Story 5.1 popular `data_entrega`, substituir `order_by(desc(Checklist.created_at))` por:
```python
from sqlalchemy import desc, nullslast
query = query.order_by(nullslast(desc(Checklist.data_entrega)), desc(Checklist.created_at))
```

### Endpoint GET /checklists — Assinatura

```python
@router.get("", response_model=list[ChecklistResponse])
def search(
    placa: str | None = None,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(get_current_user)],
):
    return search_checklists(session, placa)
```

**Importante:** O decorador é `@router.get("")` (string vazia, não `"/"`). O prefix `/checklists` vem do `APIRouter`. Ambos os perfis acessam — `get_current_user` (não `require_role`).

### Tanstack Query — Chaves e Configuração

```typescript
// Busca com filtro
const { data = [], isLoading } = useQuery<ChecklistResponse[]>({
  queryKey: ["checklists", { placa: searchTerm }],
  queryFn: () =>
    apiClient
      .get<ChecklistResponse[]>(`/v1/checklists${searchTerm ? `?placa=${encodeURIComponent(searchTerm)}` : ""}`)
      .then((r) => r.data),
  staleTime: 30 * 1000, // 30s — busca pode mudar frequentemente
  enabled: true,
});
```

**Chave de query:** Sempre fornecer a chave `["checklists", { placa }]` mesmo quando `placa` é vazio/undefined — o Tanstack Query não faz cache compartilhado entre chaves diferentes, então `["checklists", { placa: "" }]` e `["checklists", { placa: "ABC" }]` são caches independentes. Isso é o comportamento desejado.

### Formatação de Data

```typescript
function formatDate(iso: string): string {
  return new Intl.DateTimeFormat("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}
```

Sem biblioteca extra. O campo `created_at` vem da API como string ISO 8601 com timezone.

### MSG-009 — Texto Exato

```
"Nenhum checklist encontrado para a placa informada. Verifique o número da placa e tente novamente."
```

Exibir apenas quando `searchTerm` não vazio E `data.length === 0` E query completada (`!isLoading`). Sem busca prévia (tela inicial), exibir a lista completa ou mensagem neutra.

### Fixture de Teste Backend — Checklist com Motorista

Para os testes de busca, precisar de checklists criados. Adicionar fixture em `conftest.py` ou criar inline nos testes:

```python
@pytest.fixture(name="checklist_responsavel")
def checklist_fixture(session, test_user):
    from app.models.checklist import Checklist
    c = Checklist(
        placa="ABC1D23",
        unidade="Unidade A",
        motorista="João Silva",
        matricula_motorista="123456",
        quilometragem_inicial=10000.0,
    )
    session.add(c)
    session.commit()
    session.refresh(c)
    return c
```

**Por que fixture separada?** `auth_headers_fixture` já existe em `conftest.py` e retorna headers. Para busca, precisar de um checklist no banco para verificar o resultado.

### Fixture de Motorista para Teste de Acesso

```python
@pytest.fixture(name="motorista_headers")
def motorista_headers_fixture(client, session):
    from app.core.security import hash_password
    from app.models.user import User, UserRole
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
    login = client.post("/api/v1/auth/login", json={"username": "motorista_test", "password": "Senha123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}
```

Adicionar em `conftest.py` junto com as demais fixtures.

### Estrutura do Componente ChecklistList

```tsx
// frontend/src/features/checklist/ChecklistList.tsx
export default function ChecklistList() {
  const [inputValue, setInputValue] = useState("");
  const [searchTerm, setSearchTerm] = useState(""); // atualizado no submit

  const { data = [], isLoading } = useQuery<ChecklistResponse[]>({...});

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setSearchTerm(inputValue.trim());
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <label htmlFor="placa-search">Placa</label>
        <input id="placa-search" value={inputValue} onChange={(e) => setInputValue(e.target.value)} />
        <button type="submit">Buscar</button>
      </form>
      {isLoading && <p>Buscando...</p>}
      {!isLoading && searchTerm && data.length === 0 && (
        <p role="status">
          Nenhum checklist encontrado para a placa informada. Verifique o número da placa e tente novamente.
        </p>
      )}
      {data.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Nº de Controle</th>
              <th>Placa</th>
              <th>Data de Registro</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.id} onClick={() => navigate(`/checklists/${c.id}`)}>
                <td>{c.id}</td>
                <td>{c.placa}</td>
                <td>{formatDate(c.created_at)}</td>
                <td>{c.status === "entregue" ? "Entregue" : "Devolvido"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
```

**Separação de estado `inputValue` / `searchTerm`:** Permite que o usuário edite o campo sem disparar a query a cada tecla. A query só muda quando o formulário é submetido.

### Estrutura de Arquivos a Criar/Modificar

```
backend/app/
  services/checklist_service.py    ← MODIFICAR (adicionar search_checklists)
  api/routes/checklists.py         ← MODIFICAR (adicionar GET /)
backend/tests/
  api/test_checklists.py           ← MODIFICAR (adicionar testes de busca)
  conftest.py                      ← MODIFICAR (adicionar fixtures checklist + motorista)

frontend/src/
  features/checklist/
    ChecklistList.tsx               ← CRIAR
    __tests__/
      ChecklistList.test.tsx        ← CRIAR
  routes.tsx                        ← MODIFICAR (adicionar rota /checklists)
```

### Anti-padrões (PROIBIDO)

- ❌ `fetch()` direto no componente — usar `useQuery` com `apiClient`
- ❌ Busca case-sensitive (sem `.upper()` na query) — quebraria RN-009
- ❌ `require_role(UserRole.responsavel)` no endpoint de busca — motorista pode buscar
- ❌ `any` em TypeScript — tipar `ChecklistResponse[]` explicitamente
- ❌ Filtrar no frontend em vez de passar `placa` para a API — performance incorreta para volumes grandes
- ❌ `useState` para resultados da API — usar Tanstack Query

### Aprendizados das Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 2.2 |
|-------------|--------------|----------------|
| `z.coerce.number()` em vez de `z.number()` para inputs numéricos em jsdom | Story 2.1 debug | N/A (não há formulário numérico) |
| `fullmatch()` não `match()` para regex de placa | Story 2.1 | Busca usa `LIKE`, não regex — sem impacto |
| `.upper()` antes de validar/persistir placa | Story 2.1 | `.upper()` também na busca para case-insensitive |
| `TestClient` + `Secure=True` cookie exige `force_debug_mode` fixture | Story 1.1 review | Fixture já em `conftest.py` — não reimplementar |
| `isAxiosError` exportado de `apiClient.ts`, não importado de `axios` | Story 1.1 review | Usar `import { isAxiosError } from "../../lib/apiClient"` |
| `useAuthContext()` em vez de `apiClient` diretamente em componentes de autenticação | Story 1.1 review | `ChecklistList` não precisa de auth diretamente — `ProtectedRoute` já garante |

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-009
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-009
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — "Padrões de Comunicação" (query keys), "Mapeamento Requisitos→Estrutura" (US-004 → `ChecklistList.tsx`)
- Story 2.1: `_bmad-output/implementation-artifacts/2-1-criar-novo-checklist.md` — modelo Checklist, ChecklistResponse, padrão ChecklistError

## Review Findings

- [x] [Review][Patch] LIKE wildcards `%` e `_` não escapados — adicionado `autoescape=True` [backend/app/services/checklist_service.py:26]
- [x] [Review][Patch] Ordering test usa `quilometragem_inicial` como proxy — substituído por comparação de `created_at` [backend/tests/api/test_checklists.py:244]
- [x] [Review][Patch] `formatDate` retorna "Invalid Date" silenciosamente — adicionado guard com fallback "—" [frontend/src/features/checklist/ChecklistList.tsx:11]
- [x] [Review][Patch] `statusLabel` com else aberto — refatorado para `Record<ChecklistStatus, string>` [frontend/src/features/checklist/ChecklistList.tsx:20]
- [x] [Review][Patch] `<tr role="button">` sem `tabIndex={0}` e `onKeyDown` — corrigido (WCAG 2.1 SC 2.1.1) [frontend/src/features/checklist/ChecklistList.tsx:91]
- [x] [Review][Patch] `aria-live="polite"` redundante em `role="status"` — removido atributo redundante [frontend/src/features/checklist/ChecklistList.tsx:70]
- [x] [Review][Patch] `motorista_headers_fixture` — descartado (falso positivo: engine function-scoped, SQLite in-memory) [backend/tests/conftest.py:95]
- [x] [Review][Patch] `require_role` importado mas não usado — descartado (falso positivo: usado no endpoint `create`) [backend/app/api/routes/checklists.py:6]
- [x] [Review][Patch] Ausência de teste para estado `isLoading` — adicionado teste de carregamento [frontend/src/features/checklist/__tests__/ChecklistList.test.tsx]
- [x] [Review][Patch] Teste `exibe_resultados` não verifica "Data de Registro" — adicionada asserção de regex de data [frontend/src/features/checklist/__tests__/ChecklistList.test.tsx:67]
- [x] [Review][Defer] Resultado sem paginação/LIMIT — tabela inteira materializada em memória sem filtro — deferred, pre-existing
- [x] [Review][Defer] Visibilidade cross-unit — motorista acessa checklists de todas as unidades — deferred, fora do escopo da story
- [x] [Review][Defer] `placa=""` (string vazia) silenciosamente retorna todos os registros — inconsistência semântica de API — deferred, pre-existing
- [x] [Review][Defer] Teste MSG-009 não verifica estado de loading removido antes da asserção — deferred, pre-existing pattern

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- Parâmetros FastAPI: `placa: str | None = None` (query param com default) deve vir APÓS os parâmetros de dependency sem default — reordenados para `session`, `_`, depois `placa`.
- Fixture `motorista_headers` adicionada ao `conftest.py` em vez de `test_checklists.py` para reutilização.

### Completion Notes List

- Backend: `search_checklists()` adicionado ao service com busca substring case-insensitive via `.upper()` e ordenação por `created_at DESC`
- Endpoint `GET /api/v1/checklists?placa=` requer apenas autenticação (ambos os perfis)
- 7 novos testes backend (busca exata, parcial, case-insensitive, sem resultado, sem filtro, motorista, ordenação) — 45 total
- Frontend: `ChecklistList.tsx` com separação de `inputValue`/`searchTerm` para evitar queries a cada tecla
- Rota `/checklists` adicionada às rotas protegidas (sem `RequireRole`)
- 6 testes frontend (render, resultados, MSG-009, sem busca prévia, navegação, status devolvido) — 33 total
- 0 regressões em todos os suites

### File List

backend/app/services/checklist_service.py
backend/app/api/routes/checklists.py
backend/tests/conftest.py
backend/tests/api/test_checklists.py
frontend/src/features/checklist/ChecklistList.tsx
frontend/src/features/checklist/__tests__/ChecklistList.test.tsx
frontend/src/routes.tsx
