# Story 2.1: Criar Novo Checklist

Status: done

## Story

Como Responsável,
quero criar um novo checklist informando os dados gerais do veículo,
para que o processo de entrega seja iniciado com todas as informações de identificação registradas.

## Acceptance Criteria

1. Formulário exibe campos: Nº de Controle (auto-gerado), Placa, Unidade, Subunidade (opcional), Motorista, Matrícula, Quilometragem Inicial.
2. Campos obrigatórios: Placa, Unidade, Motorista, Matrícula, Quilometragem Inicial — ausência exibe MSG-005.
3. Placa validada no formato Mercosul (ABC1D23) ou antigo (ABC-1234) — formato inválido exibe MSG-006.
4. Matrícula do motorista aceita apenas valores numéricos — valor não numérico exibe MSG-007.
5. Sistema não permite criar checklist de entrega se já existe entrega aberta (status="entregue", is_locked=True) para o mesmo veículo (placa) — exibe MSG-008.
6. Criação bem-sucedida retorna 201 com `ChecklistResponse` e redireciona para visualização do checklist criado.
7. Apenas Responsável pode criar checklists — Motorista recebe 403 com MSG-026.

## Tasks / Subtasks

- [ ] **T1 — Model Checklist (AC: 1, 5, 6)** — `backend/app/models/checklist.py`
  - [ ] Definir `ChecklistStatus` enum: `entregue`, `devolvido`
  - [ ] Definir `Checklist` (SQLModel, `table=True`):
    - `id`, `placa` (indexado), `unidade`, `subunidade` (nullable), `motorista`, `matricula_motorista`, `quilometragem_inicial` (float)
    - `status: ChecklistStatus = entregue`, `is_locked: bool = False`
    - `data_entrega: datetime | None = None`, `created_at: datetime`
  - [ ] Importar `Checklist` em `database.py` para que `create_db_and_tables()` crie a tabela

- [ ] **T2 — Schemas Checklist (AC: 1, 2, 3, 4, 6)** — `backend/app/schemas/checklist.py`
  - [ ] `ChecklistCreate`: campos obrigatórios (placa, unidade, motorista, matricula_motorista, quilometragem_inicial) + subunidade opcional
  - [ ] `ChecklistResponse`: todos os campos + `id`, `status`, `is_locked`, `created_at`
  - [ ] Validação Pydantic em `ChecklistCreate`:
    - `placa`: regex `^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}-[0-9]{4}$` com `detail="MSG-006"`
    - `matricula_motorista`: `str.isdigit()` validado via `@field_validator` com `detail="MSG-007"`

- [ ] **T3 — ChecklistError + checklist_service.py (AC: 2, 5)** — `backend/app/services/checklist_service.py`
  - [ ] Criar `ChecklistError(Exception)` com mesma assinatura de `UserError` (status_code, detail, message, fields)
  - [ ] Registrar handler em `main.py`: `@app.exception_handler(ChecklistError)`
  - [ ] `create_checklist(session, data: ChecklistCreate) -> Checklist`:
    - RN-008: `SELECT * FROM checklists WHERE placa=? AND status='entregue' AND is_locked=True` — se encontrado, levanta `ChecklistError(400, "MSG-008", ...)`
    - Persiste `Checklist` com `status="entregue"`, `is_locked=False` (lock ocorre no save completo, Epic 3)
    - Retorna checklist criado

- [ ] **T4 — Router /checklists (AC: 6, 7)** — `backend/app/api/routes/checklists.py`
  - [ ] `POST /api/v1/checklists` (requer `require_role(UserRole.responsavel)`):
    - Recebe `ChecklistCreate`
    - Delega para `checklist_service.create_checklist()`
    - Retorna `ChecklistResponse` com status 201
  - [ ] Registrar router em `main.py`

- [ ] **T5 — Testes backend (AC: 2, 3, 4, 5, 6, 7)** — `backend/tests/api/test_checklists.py`
  - [ ] `test_create_checklist_success`: POST /checklists placa Mercosul → 201 + response com id
  - [ ] `test_create_checklist_placa_antiga`: POST com placa "ABC-1234" → 201 (formato antigo aceito)
  - [ ] `test_create_checklist_placa_invalida`: POST com placa "12345" → 422 + `detail == "MSG-006"`
  - [ ] `test_create_checklist_matricula_nao_numerica`: POST com matricula "ABC" → 422 + `detail == "MSG-007"`
  - [ ] `test_create_checklist_entrega_duplicada`: duas entregas com mesma placa (primeira com is_locked=True) → 400 + `detail == "MSG-008"`
  - [ ] `test_create_checklist_permite_apos_devolucao`: entrega devolvida → nova entrega permitida
  - [ ] `test_create_checklist_motorista_proibido`: POST autenticado como motorista → 403
  - [ ] `test_create_checklist_subunidade_opcional`: POST sem subunidade → 201

- [ ] **T6 — Frontend: Zod schema + ChecklistForm (AC: 1, 2, 3, 4)** — `frontend/src/features/checklist/`
  - [ ] `checklistSchema.ts` — Zod schema para informações gerais:
    - `placa`: regex `/^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}-[0-9]{4}$/` com mensagem MSG-006
    - `unidade`, `motorista`: `string().min(1)`
    - `subunidade`: `string().optional()`
    - `matricula_motorista`: `string().regex(/^\d+$/)` com mensagem MSG-007
    - `quilometragem_inicial`: `number().min(0)`
  - [ ] `ChecklistForm.tsx` — seção de Informações Gerais:
    - 7 campos com labels em português
    - `onSubmit` → `POST /api/v1/checklists` via `apiClient`
    - Sucesso: navega para `/checklists/{id}` (view placeholder por enquanto)
    - Erro 400 MSG-008: exibe alerta "Já existe entrega aberta para esta placa"
    - Erro 422 (placa/matrícula): exibe mensagem no campo específico

- [ ] **T7 — Rota /checklists/new (AC: 7)** — `frontend/src/routes.tsx`
  - [ ] Adicionar rota `/checklists/new` dentro de `ProtectedRoute` com `RequireRole role="responsavel"`
  - [ ] Criar placeholder `ChecklistView` (`/checklists/:id`) dentro de `ProtectedRoute`

- [ ] **T8 — Testes frontend (AC: 1, 2, 3, 4, 5)** — `frontend/src/features/checklist/__tests__/ChecklistForm.test.tsx`
  - [ ] `test_renders_informacoes_gerais`: formulário exibe todos os 7 campos
  - [ ] `test_placa_mercosul_valida`: Zod aceita "ABC1D23"
  - [ ] `test_placa_invalida_bloqueada`: Zod bloqueia "12345" com MSG-006
  - [ ] `test_matricula_nao_numerica_bloqueada`: Zod bloqueia "ABC" com MSG-007
  - [ ] `test_submit_success_redireciona`: mock POST 201 → verifica navegação para `/checklists/1`
  - [ ] `test_entrega_duplicada_exibe_msg_008`: mock POST 400 MSG-008 → exibe alerta

### Review Findings

- [x] [Review][Decision] Campo "Nº de Controle (auto-gerado)" ausente do formulário — decisão A: campo somente leitura com placeholder "Gerado automaticamente"
- [x] [Review][Decision] Campos obrigatórios ausentes retornam 422 padrão do FastAPI, não MSG-005 — decisão A: handler de `RequestValidationError` adicionado em `main.py`
- [x] [Review][Patch] Zod de campos obrigatórios usa mensagens genéricas, não o texto de MSG-005 — AC-2 [`frontend/src/features/checklist/checklistSchema.ts`]
- [x] [Review][Patch] `quilometragem_inicial` sem validação de mínimo no backend — service aceita valores negativos [`backend/app/services/checklist_service.py`]
- [x] [Review][Patch] Placa Zod: `.regex()` executa antes de `.transform(toUpperCase())` — input em minúsculo falha no frontend mesmo sendo aceito pelo backend [`frontend/src/features/checklist/checklistSchema.ts`]
- [x] [Review][Patch] Input de quilometragem sem atributo `min="0"` no HTML — browser permite negativos via spinner [`frontend/src/features/checklist/ChecklistForm.tsx`]
- [x] [Review][Defer] `data_entrega` ausente do `ChecklistResponse` — campo sempre `None` nesta story; incluir quando for utilizado — deferred, pré-existente
- [x] [Review][Defer] Normalização uppercase da placa não enforçada em nível de BD — inserções externas podem bypassar RN-008 — deferred, pré-existente
- [x] [Review][Defer] `ChecklistError` não chama `super().__init__()` — mesmo padrão de `UserError` (story 1.2); corrigir em refactor cross-story — deferred, pré-existente

## Dev Notes

### Código Reutilizável das Stories 1.x — NÃO REIMPLEMENTAR

| Item | Localização | Reutiliza Como |
|------|-------------|----------------|
| `require_role(UserRole.responsavel)` | `backend/app/core/deps.py` | Dependency para `POST /checklists` |
| `get_current_user` | `backend/app/core/deps.py` | Dependency base |
| `UserError` pattern | `backend/app/services/user_service.py` | Copiar estrutura para `ChecklistError` |
| Exception handler em `main.py` | `backend/app/main.py` | Adicionar `@app.exception_handler(ChecklistError)` |
| `apiClient` | `frontend/src/lib/apiClient.ts` | POST /checklists |
| `RequireRole` | `frontend/src/components/RequireRole.tsx` | Proteção da rota |
| `AxiosError` pattern | `LoginForm.tsx`, `RegisterForm.tsx` | Mesmo tratamento de erros |

### Modelo Checklist — campos desta story e futuros

```python
class Checklist(SQLModel, table=True):
    __tablename__ = "checklists"
    id: int | None = Field(default=None, primary_key=True)
    # Story 2.1 — Informações Gerais
    placa: str = Field(index=True)
    unidade: str
    subunidade: str | None = None
    motorista: str
    matricula_motorista: str  # numérica, do motorista (diferente da matricula do user)
    quilometragem_inicial: float
    status: ChecklistStatus = Field(default=ChecklistStatus.entregue)
    is_locked: bool = Field(default=False)
    data_entrega: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Stories futuras (não implementar agora):
    # quilometragem_final, data_devolucao, observacoes — Story 4.x
    # entrega_id (FK) — Story 4.1
```

**IMPORTANTE:** `matricula_motorista` é a matrícula do motorista informada no formulário (RN-007 — somente numérica). É diferente de `User.matricula` (cadastro de usuário, RN-003). Não confundir.

### RN-008 — Lógica de Bloqueio de Entrega Duplicada

Entrega duplicada = placa com entrega `is_locked=True` e `status="entregue"`. Uma entrega não bloqueada (`is_locked=False`) ainda está em preenchimento e não bloqueia nova entrega.

```python
open_delivery = session.exec(
    select(Checklist).where(
        Checklist.placa == data.placa,
        Checklist.status == ChecklistStatus.entregue,
        Checklist.is_locked == True,
    )
).first()
if open_delivery:
    raise ChecklistError(
        status_code=400,
        detail="MSG-008",
        message=f"Já existe um checklist de entrega aberto para o veículo de placa {data.placa}. Conclua a devolução antes de registrar nova entrega.",
        fields=["placa"],
    )
```

### Validação de Placa — Regex Duplo (RN-006)

```python
# Mercosul: ABC1D23 (3 letras, 1 dígito, 1 letra ou dígito, 2 dígitos)
# Antigo:   ABC-1234 (3 letras, hífen, 4 dígitos)
PLACA_REGEX = re.compile(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$|^[A-Z]{3}-[0-9]{4}$')
```

No Pydantic v2, validar via `@field_validator('placa', mode='before')` com `fullmatch()`. Usar `fullmatch()` (não `match()`) — lição do code review da Story 1.2.

### Pydantic v2 — Validators no Schema

```python
from pydantic import field_validator

class ChecklistCreate(BaseModel):
    placa: str
    matricula_motorista: str

    @field_validator('placa')
    @classmethod
    def validate_placa(cls, v: str) -> str:
        if not PLACA_REGEX.fullmatch(v.upper()):
            raise ValueError('MSG-006')
        return v.upper()

    @field_validator('matricula_motorista')
    @classmethod
    def validate_matricula(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('MSG-007')
        return v
```

**Atenção:** `ValueError` no Pydantic v2 é capturado como `RequestValidationError` pelo FastAPI, que retorna 422. O `detail` neste caso vem do `ValidationError` padrão. Para retornar `MSG-006` e `MSG-007` no formato `{detail, message, fields}`, há duas opções:
- Opção A (simples): sobrescrever o `exception_handler` do `RequestValidationError` em `main.py`
- Opção B: validar em `checklist_service.py` com `ChecklistError` ao invés de Pydantic

**Recomendação: Opção B** para consistência com o padrão de `user_service.py`. Pydantic valida campos obrigatórios e tipos (int, str), service valida regras de negócio (formato placa, numérico).

### Estrutura de Arquivos a Criar/Modificar

```
backend/app/
  models/checklist.py         ← CRIAR
  schemas/checklist.py        ← CRIAR
  services/checklist_service.py ← CRIAR
  api/routes/checklists.py    ← CRIAR
  database.py                 ← MODIFICAR (importar Checklist para criar tabela)
  main.py                     ← MODIFICAR (registrar router + exception handler)
backend/tests/api/
  test_checklists.py          ← CRIAR

frontend/src/
  features/checklist/
    ChecklistForm.tsx          ← CRIAR
    checklistSchema.ts         ← CRIAR
    __tests__/
      ChecklistForm.test.tsx   ← CRIAR
  types/
    checklist.ts               ← CRIAR (ChecklistResponse type)
  routes.tsx                   ← MODIFICAR
```

### Convenções Estabelecidas (não desviar)

- Tabela: `checklists` (snake_case plural)
- Colunas: `snake_case` — `matricula_motorista`, `quilometragem_inicial`, `is_locked`
- Enum no banco: `ChecklistStatus` com valores `"entregue"` e `"devolvido"`
- Resposta de erro: `{"detail": "MSG-XXX", "message": "...", "fields": [...]}`
- Componente: `ChecklistForm.tsx` (PascalCase)
- Schema Zod: arquivo separado `checklistSchema.ts` (padrão de `registerSchema.ts`)

### Project Structure Notes

- `checklist_service.py` é o componente mais importante do sistema — conterá validação de RN-005 a RN-025. Esta story cria a fundação que todas as demais stories do checklist (Epics 3, 4, 5) vão estender.
- Não implementar lock (`is_locked=True`) nesta story — o lock ocorre no salvamento completo (Story 5.1, RN-021/022). Nesta story, checklist é criado com `is_locked=False`.

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-005, RN-006, RN-007, RN-008
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-005, MSG-006, MSG-007, MSG-008
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — seções "Arquitetura de Dados", "Estrutura de Diretórios", "Mapeamento Requisitos→Estrutura"
- Story 1.2: `_bmad-output/implementation-artifacts/1-2-cadastro-de-usuario.md` — padrão `UserError` a replicar

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `z.number()` + `valueAsNumber: true` em jsdom causa NaN → substituído por `z.coerce.number()`
- Regex `/entrega aberta/i` no teste não batia com "entrega aberto" (masculino) → corrigido para `/checklist de entrega aberto/i`

### Completion Notes List

- Checklist model criado com status enum (entregue/devolvido) e is_locked flag
- checklist_service.py com RN-006 (fullmatch placa), RN-007 (matrícula numérica), RN-008 (entrega duplicada bloqueada)
- ChecklistError com handler global em main.py — mesmo padrão de UserError
- POST /api/v1/checklists com require_role(responsavel)
- database.py atualizado para importar Checklist e criar tabela no startup
- 8 testes backend + 4 testes frontend, 0 regressões

### File List

backend/app/models/checklist.py
backend/app/schemas/checklist.py
backend/app/services/checklist_service.py
backend/app/api/routes/checklists.py
backend/app/database.py
backend/app/main.py
backend/tests/api/test_checklists.py
frontend/src/types/checklist.ts
frontend/src/features/checklist/checklistSchema.ts
frontend/src/features/checklist/ChecklistForm.tsx
frontend/src/features/checklist/__tests__/ChecklistForm.test.tsx
frontend/src/routes.tsx
