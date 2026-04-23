# Story 3.1: Preencher Checklist de Entrega

Status: done

## Story

Como Responsável,
quero verificar os 20 itens do checklist de entrega, registrar o nível de combustível e informar a data/horário,
para que as condições do veículo no momento da entrega fiquem documentadas.

## Acceptance Criteria

1. Exibe 20 itens de verificação organizados em duas colunas: "Documentação/Equipamentos" (itens 1–10) e "Condições do Veículo" (itens 11–20).
2. Cada item deve ser marcado como **OK** ou **Não OK** via botões de rádio — nenhum pode ficar sem resposta. Ao tentar salvar com itens pendentes, exibir MSG-010.
3. Nível de combustível com seleção exclusiva: 1/4, 2/4, 3/4 ou 4/4 (radio buttons). Ao tentar salvar sem seleção, exibir MSG-011.
4. Data e horário da entrega obrigatórios (campo `datetime-local`). Ao tentar salvar sem preencher, exibir MSG-012.
5. Página `/checklists/:id` exibe o formulário de entrega (ChecklistItems + FuelLevel + Data/Hora) para checklists não bloqueados.
6. Endpoint `PATCH /api/v1/checklists/{id}/entrega` persiste itens, nível de combustível e data da entrega. Requer role `responsavel`.

## Tasks / Subtasks

- [x] **T1 — Estender modelo `Checklist` e schema (AC: 6)**
  - [x] Em `backend/app/models/checklist.py`: adicionar `itens: list | None = Field(default=None, sa_column=Column(JSON))` e `nivel_combustivel: str | None = None`
  - [x] Adicionar import: `from sqlalchemy import JSON` e `from sqlmodel import Column`
  - [x] Em `backend/app/schemas/checklist.py`: adicionar `ChecklistItemData`, `ChecklistEntregaUpdate`, e estender `ChecklistResponse` com `itens`, `nivel_combustivel`, `data_entrega`

- [x] **T2 — Service `update_entrega` (AC: 6)**
  - [x] Em `backend/app/services/checklist_service.py`: adicionar `update_entrega(session, checklist_id, data) -> Checklist`
  - [x] Validar: checklist existe → 404 se não; `is_locked == True` → ChecklistError 400 "MSG-026"
  - [x] Persistir: `checklist.itens = [{"nome": item.nome, "status": item.status} for item in data.itens]`, `checklist.nivel_combustivel = data.nivel_combustivel`, `checklist.data_entrega = data.data_entrega`

- [x] **T3 — Endpoint `PATCH /{id}/entrega` (AC: 6)**
  - [x] Em `backend/app/api/routes/checklists.py`: adicionar `@router.patch("/{checklist_id}/entrega", response_model=ChecklistResponse)`
  - [x] Requer `require_role(UserRole.responsavel)` — apenas responsável preenche
  - [x] Delega para `update_entrega(session, checklist_id, body)`
  - [x] Handler de `ChecklistError` existente já captura 404/400

- [x] **T4 — Testes backend (AC: 6)**
  - [x] `test_update_entrega_ok`: PATCH com todos os 20 itens, combustível e data → 200 + checklist atualizado
  - [x] `test_update_entrega_checklist_nao_encontrado`: id inexistente → 404
  - [x] `test_update_entrega_locked`: checklist com `is_locked=True` → 400 MSG-026
  - [x] `test_update_entrega_motorista_proibido`: autenticado como motorista → 403 MSG-026
  - [x] `test_update_entrega_sem_autenticacao`: sem token → 401

- [x] **T5 — Tipos TypeScript (AC: 1–5)**
  - [x] Em `frontend/src/types/checklist.ts`: adicionar `ChecklistItemStatus`, `ChecklistItemData`, `NivelCombustivel`
  - [x] Estender `ChecklistResponse` com `itens: ChecklistItemData[] | null`, `nivel_combustivel: NivelCombustivel | null`, `data_entrega: string | null`

- [x] **T6 — Componente `ChecklistItems.tsx` (AC: 1, 2)**
  - [x] Criar `frontend/src/features/checklist/ChecklistItems.tsx`
  - [x] Constante `CHECKLIST_ITEMS` com 20 itens e `coluna: "esquerda" | "direita"`
  - [x] Recebe `control: Control<ChecklistEntregaData>` do formulário pai
  - [x] Renderiza duas colunas; cada item tem radio buttons OK e Não OK com IDs acessíveis
  - [x] Erro por item: exibir quando status inválido e formulário foi submetido

- [x] **T7 — Componente `FuelLevel.tsx` (AC: 3)**
  - [x] Criar `frontend/src/features/checklist/FuelLevel.tsx`
  - [x] Recebe `control: Control<ChecklistEntregaData>`
  - [x] 4 radio buttons em linha: "1/4", "2/4", "3/4", "4/4" — seleção exclusiva via Controller

- [x] **T8 — Schema Zod `checklistEntregaSchema` (AC: 2, 3, 4)**
  - [x] Em `frontend/src/features/checklist/checklistSchema.ts`: adicionar `checklistEntregaSchema`
  - [x] `itens`: array de 20 objetos com `status: z.enum(["ok", "nao_ok"])`
  - [x] `nivel_combustivel`: `z.enum(["1/4", "2/4", "3/4", "4/4"])`
  - [x] `data_entrega`: `z.string().min(1, "Informe a data e o horário da entrega.")`

- [x] **T9 — `ChecklistView.tsx` (AC: 5)**
  - [x] Criar `frontend/src/features/checklist/ChecklistView.tsx`
  - [x] `useQuery(["checklists", id])` para carregar checklist via `GET /v1/checklists/:id`
  - [x] Se `is_locked == true`: renderizar view read-only com lista de itens e combustível
  - [x] Se `is_locked == false`: formulário editável com ChecklistItems, FuelLevel, datetime-local
  - [x] Botão "Salvar" desabilitado (Story 5.1 habilitará)
  - [x] Informações gerais exibidas como read-only no topo

- [x] **T10 — Atualizar `routes.tsx` (AC: 5)**
  - [x] Substituir `ChecklistView` placeholder pelo componente real de `features/checklist/ChecklistView`

- [x] **T11 — Testes frontend (AC: 1–5)**
  - [x] `ChecklistItems.test.tsx`: renderiza 20 itens em 2 colunas, selecionar OK, selecionar Não OK (6 testes)
  - [x] `FuelLevel.test.tsx`: renderiza 4 opções, seleção exclusiva funciona (3 testes)
  - [x] `ChecklistView.test.tsx`: exibe infos gerais, formulário editável, botão disabled, read-only locked, loading, 20 itens (6 testes)

## Dev Notes

### Os 20 Itens do Checklist (extraídos de `modelo.png`)

```typescript
// frontend/src/features/checklist/ChecklistItems.tsx
export const CHECKLIST_ITEMS: { nome: string; coluna: "esquerda" | "direita" }[] = [
  // Coluna Esquerda — Documentação/Equipamentos (itens 1–10)
  { nome: "Documento Veicular", coluna: "esquerda" },
  { nome: "Chave de Roda", coluna: "esquerda" },
  { nome: "Macaco", coluna: "esquerda" },
  { nome: "Triângulo de Sinalização", coluna: "esquerda" },
  { nome: "Estepe", coluna: "esquerda" },
  { nome: "Extintor de Incêndio", coluna: "esquerda" },
  { nome: "Cintos de Segurança", coluna: "esquerda" },
  { nome: "Luzes de Freios", coluna: "esquerda" },
  { nome: "Nível de água (aditivo)", coluna: "esquerda" },
  { nome: "Óleo de motor", coluna: "esquerda" },
  // Coluna Direita — Condições do Veículo (itens 11–20)
  { nome: "Luzes de Posição (faroletes)", coluna: "direita" },
  { nome: "Faróis (alto e baixo)", coluna: "direita" },
  { nome: "Luzes de Seta (pisca-alerta)", coluna: "direita" },
  { nome: "Luz de Placa", coluna: "direita" },
  { nome: "Luz de Ré", coluna: "direita" },
  { nome: "Ar Condicionado", coluna: "direita" },
  { nome: "Buzina", coluna: "direita" },
  { nome: "Rádio/Multimídia", coluna: "direita" },
  { nome: "Fluidos de Freios", coluna: "direita" },
  { nome: "Limpadores de Para-brisa", coluna: "direita" },
];
```

**Nota:** O 20º item ("Limpadores de Para-brisa") foi inferido por não ser claramente legível na imagem de referência — confirmar com o usuário se necessário.

### Armazenamento dos Itens: JSON no modelo Checklist

O arquitetura menciona `checklist_item.py` como modelo separado, mas esta story armazena os itens como JSON direto no `Checklist.itens` — padrão consistente com `damage_point.py` que também usa JSON. Motivo: itens são lista estática (sempre os mesmos 20 nomes), sem necessidade de query relacional. Future refactor para tabela separada se requisito surgir.

```python
# backend/app/models/checklist.py — campos a adicionar
from sqlalchemy import JSON
from sqlmodel import Column, Field

class Checklist(SQLModel, table=True):
    ...
    itens: list | None = Field(default=None, sa_column=Column(JSON))
    nivel_combustivel: str | None = None
    # data_entrega: datetime | None = None  ← JÁ EXISTE no modelo atual
```

### Schemas Backend

```python
# backend/app/schemas/checklist.py

class ChecklistItemData(BaseModel):
    nome: str
    status: Literal["ok", "nao_ok"] | None = None

class ChecklistEntregaUpdate(BaseModel):
    itens: list[ChecklistItemData]
    nivel_combustivel: Literal["1/4", "2/4", "3/4", "4/4"]
    data_entrega: datetime

class ChecklistResponse(BaseModel):  # estender campos existentes
    ...
    itens: list[ChecklistItemData] | None = None
    nivel_combustivel: str | None = None
    data_entrega: datetime | None = None
    model_config = {"from_attributes": True}
```

### Service `update_entrega`

```python
# backend/app/services/checklist_service.py
def update_entrega(session: Session, checklist_id: int, data: ChecklistEntregaUpdate) -> Checklist:
    checklist = session.get(Checklist, checklist_id)
    if not checklist:
        raise ChecklistError(status_code=404, detail="NOT_FOUND", message="Checklist não encontrado.", fields=[])
    if checklist.is_locked:
        raise ChecklistError(status_code=400, detail="MSG-026", message="Checklist bloqueado.", fields=[])
    checklist.itens = [{"nome": item.nome, "status": item.status} for item in data.itens]
    checklist.nivel_combustivel = data.nivel_combustivel
    checklist.data_entrega = data.data_entrega
    session.add(checklist)
    session.commit()
    session.refresh(checklist)
    return checklist
```

### Endpoint Backend

```python
# backend/app/api/routes/checklists.py
@router.patch("/{checklist_id}/entrega", response_model=ChecklistResponse)
def update_entrega(
    checklist_id: int,
    body: ChecklistEntregaUpdate,
    session: Annotated[Session, Depends(get_session)],
    _: Annotated[User, Depends(require_role(UserRole.responsavel))],
):
    return checklist_service.update_entrega(session, checklist_id, body)
```

**Importante:** Handler de `ChecklistError` existente em `main.py` já cuida de 404/400 — sem handler extra necessário.

### Schema Zod (Frontend)

```typescript
// frontend/src/features/checklist/checklistSchema.ts
import { z } from "zod";

export const checklistItemSchema = z.object({
  nome: z.string(),
  status: z.enum(["ok", "nao_ok"], { message: "Selecione OK ou Não OK" }),
});

export const checklistEntregaSchema = z.object({
  itens: z.array(checklistItemSchema).length(20),
  nivel_combustivel: z.enum(["1/4", "2/4", "3/4", "4/4"], {
    message: "Selecione o nível de combustível do veículo (1/4, 2/4, 3/4 ou 4/4).",
  }),
  data_entrega: z.string().min(1, "Informe a data e o horário da entrega."),
});

export type ChecklistEntregaData = z.infer<typeof checklistEntregaSchema>;
```

### `ChecklistView.tsx` — Estrutura

```typescript
// frontend/src/features/checklist/ChecklistView.tsx
export default function ChecklistView() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: checklist, isLoading } = useQuery<ChecklistResponse>({
    queryKey: ["checklists", id],
    queryFn: () => apiClient.get<ChecklistResponse>(`/v1/checklists/${id}`).then(r => r.data),
  });

  const { control, register, handleSubmit, formState: { errors } } = useForm<ChecklistEntregaData>({
    resolver: zodResolver(checklistEntregaSchema),
    defaultValues: { itens: CHECKLIST_ITEMS.map(i => ({ nome: i.nome, status: undefined })) },
  });

  if (isLoading) return <p>Carregando...</p>;
  if (!checklist) return <p>Checklist não encontrado.</p>;

  return (
    <div>
      {/* Informações Gerais read-only */}
      <section>
        <h2>Informações Gerais</h2>
        {/* placa, unidade, motorista como read-only */}
      </section>

      {checklist.is_locked ? (
        /* View read-only dos itens */
      ) : (
        <form onSubmit={handleSubmit(onSubmit)}>
          <ChecklistItems control={control} errors={errors} />
          <FuelLevel control={control} error={errors.nivel_combustivel} />
          <div>
            <label htmlFor="data_entrega">Data e Horário da Entrega</label>
            <input id="data_entrega" type="datetime-local" {...register("data_entrega")} />
            {errors.data_entrega && <span>{errors.data_entrega.message}</span>}
          </div>
          <button type="submit" disabled title="Salvar disponível na Story 5.1">
            Salvar
          </button>
        </form>
      )}
    </div>
  );
}
```

**Nota:** O botão Salvar fica desabilitado até Story 5.1. O `onSubmit` pode ser um no-op ou chamar o PATCH endpoint (que já existe no backend). Implementar o PATCH call para que Story 5.1 só precise adicionar validação e confirmação.

### Tipos TypeScript

```typescript
// frontend/src/types/checklist.ts (extensão)
export type ChecklistItemStatus = "ok" | "nao_ok";
export type NivelCombustivel = "1/4" | "2/4" | "3/4" | "4/4";

export interface ChecklistItemData {
  nome: string;
  status: ChecklistItemStatus | null;
}

// Estender ChecklistResponse existente:
export interface ChecklistResponse {
  // ... campos existentes ...
  itens: ChecklistItemData[] | null;
  nivel_combustivel: NivelCombustivel | null;
  data_entrega: string | null;
}
```

### Padrão React Hook Form com Controller

```typescript
// ChecklistItems.tsx — usar Controller para radio buttons
import { Controller, Control } from "react-hook-form";
import type { ChecklistEntregaData } from "./checklistSchema";

interface ChecklistItemsProps {
  control: Control<ChecklistEntregaData>;
}

// Para cada item:
<Controller
  name={`itens.${index}.status`}
  control={control}
  render={({ field }) => (
    <fieldset>
      <legend>{item.nome}</legend>
      <label>
        <input type="radio" value="ok" checked={field.value === "ok"} onChange={() => field.onChange("ok")} />
        OK
      </label>
      <label>
        <input type="radio" value="nao_ok" checked={field.value === "nao_ok"} onChange={() => field.onChange("nao_ok")} />
        Não OK
      </label>
    </fieldset>
  )}
/>
```

### Fixture de Teste Backend

```python
# backend/tests/conftest.py — adicionar fixture para testes T4
@pytest.fixture(name="checklist_entrega_payload")
def checklist_entrega_payload_fixture():
    from datetime import datetime, timezone
    return {
        "itens": [{"nome": nome, "status": "ok"} for nome in [
            "Documento Veicular", "Chave de Roda", "Macaco", "Triângulo de Sinalização",
            "Estepe", "Extintor de Incêndio", "Cintos de Segurança", "Luzes de Freios",
            "Nível de água (aditivo)", "Óleo de motor",
            "Luzes de Posição (faroletes)", "Faróis (alto e baixo)", "Luzes de Seta (pisca-alerta)",
            "Luz de Placa", "Luz de Ré", "Ar Condicionado", "Buzina",
            "Rádio/Multimídia", "Fluidos de Freios", "Limpadores de Para-brisa",
        ]],
        "nivel_combustivel": "3/4",
        "data_entrega": datetime.now(timezone.utc).isoformat(),
    }
```

### Dependências e Reutilização

| Item | Localização | Uso |
|------|-------------|-----|
| `Checklist` model | `backend/app/models/checklist.py` | Estender com `itens`, `nivel_combustivel` |
| `data_entrega` | `backend/app/models/checklist.py:24` | JÁ EXISTE — não recriar |
| `ChecklistError` | `backend/app/services/checklist_service.py:12` | Reutilizar para 404/400 |
| `require_role` | `backend/app/core/deps.py` | Dependency do PATCH endpoint |
| `checklistInfoSchema` | `frontend/src/features/checklist/checklistSchema.ts` | Já existe — adicionar `checklistEntregaSchema` no mesmo arquivo |
| `apiClient` | `frontend/src/lib/apiClient.ts` | GET e PATCH do checklist |
| `ProtectedRoute` | `frontend/src/components/ProtectedRoute.tsx` | Já envolve `/checklists/:id` em routes.tsx |
| `ChecklistResponse` type | `frontend/src/types/checklist.ts` | Estender com novos campos |

### Anti-padrões (PROIBIDO)

- ❌ Criar `checklist_item.py` como tabela separada — usar JSON em `Checklist.itens`
- ❌ `useState` para resultado de GET — usar `useQuery`
- ❌ `fetch()` direto — usar `apiClient`
- ❌ `any` em TypeScript
- ❌ Validação MSG-010/011/012 no PATCH endpoint backend — estas validações ficam em Story 5.1 (salvar)
- ❌ Botão Salvar funcional — Story 5.1 habilita o save real
- ❌ Recriar o campo `data_entrega` no modelo — já existe

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 3.1 |
|-------------|--------------|----------------|
| `z.coerce.number()` para campos numéricos em jsdom | Story 2.1 debug | N/A (sem campo numérico novo nesta story) |
| `fullmatch()` não `match()` para regex | Story 2.1 | N/A |
| `autoescape=True` em `.contains()` | Story 2.2 review | N/A (não há busca nesta story) |
| `isAxiosError` importado de `apiClient.ts` | Story 1.1 review | Usar `import { isAxiosError } from "../../lib/apiClient"` |
| Parâmetros FastAPI: dependencies ANTES de query params opcionais | Story 2.2 debug | `checklist_id: int` no path, depois `session`, depois `_` (role) — verificar ordem |
| `aria-live="polite"` redundante em `role="status"` | Story 2.2 review | Não adicionar `aria-live` em elementos com `role="status"` |
| `tabIndex={0}` + `onKeyDown` em elementos clicáveis não-button | Story 2.2 review | Aplicar em `<tr>` ou elementos similares se usados em ChecklistView |

### Estrutura de Arquivos

```
backend/app/
  models/checklist.py           ← MODIFICAR (adicionar itens, nivel_combustivel)
  schemas/checklist.py          ← MODIFICAR (ChecklistItemData, ChecklistEntregaUpdate, estender Response)
  services/checklist_service.py ← MODIFICAR (adicionar update_entrega)
  api/routes/checklists.py      ← MODIFICAR (PATCH /{id}/entrega)
backend/tests/
  conftest.py                   ← MODIFICAR (fixture checklist_entrega_payload)
  api/test_checklists.py        ← MODIFICAR (5 novos testes T4)

frontend/src/
  types/checklist.ts                                ← MODIFICAR (novos tipos)
  features/checklist/
    ChecklistItems.tsx                              ← CRIAR
    FuelLevel.tsx                                   ← CRIAR
    ChecklistView.tsx                               ← CRIAR (substituir placeholder)
    checklistSchema.ts                              ← MODIFICAR (checklistEntregaSchema)
    __tests__/
      ChecklistItems.test.tsx                       ← CRIAR
      FuelLevel.test.tsx                            ← CRIAR
      ChecklistView.test.tsx                        ← CRIAR
  routes.tsx                                        ← MODIFICAR (import ChecklistView real)
```

### Referências

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-010, RN-011, RN-012
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-010, MSG-011, MSG-012
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — "Arquitetura de Dados" (JSON), "Arquitetura Frontend" (React Hook Form, Controller), "Mapeamento US-005"
- Imagem de referência: `modelo.png` (raiz do projeto) — layout visual do checklist com os 20 itens
- Story 2.1: `_bmad-output/implementation-artifacts/2-1-criar-novo-checklist.md` — padrão ChecklistError, ChecklistResponse
- Story 2.2: `_bmad-output/implementation-artifacts/2-2-buscar-checklist-por-placa.md` — padrão PATCH endpoint, fixtures de teste

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.6

### Debug Log References

- `getByRole("radio", { name: "OK" })` falha quando há múltiplos rádios com o mesmo label — corrigido para `getAllByRole` nos testes de ChecklistItems.

### Completion Notes List

- Backend: modelo `Checklist` estendido com `itens` (JSON) e `nivel_combustivel`; `data_entrega` já existia
- `ChecklistItemData`, `ChecklistEntregaUpdate` adicionados ao schema; `ChecklistResponse` extendido
- Service `update_entrega` com validação 404/locked; endpoint `PATCH /{checklist_id}/entrega` com `require_role(responsavel)`
- 5 novos testes backend (ok, 404, locked, motorista, sem-auth) — 50 total, zero regressões
- Frontend: `ChecklistItems.tsx` com 20 itens em 2 colunas via Controller; `FuelLevel.tsx` com 4 opções
- `ChecklistView.tsx` com modo editável + read-only (is_locked); botão Salvar desabilitado até Story 5.1
- Schema Zod `checklistEntregaSchema` + tipos TypeScript `ChecklistItemData`, `NivelCombustivel`
- 16 novos testes frontend em 3 arquivos — 49 total, zero regressões

### File List

backend/app/models/checklist.py
backend/app/schemas/checklist.py
backend/app/services/checklist_service.py
backend/app/api/routes/checklists.py
backend/tests/conftest.py
backend/tests/api/test_checklists.py
frontend/src/types/checklist.ts
frontend/src/features/checklist/checklistSchema.ts
frontend/src/features/checklist/ChecklistItems.tsx
frontend/src/features/checklist/FuelLevel.tsx
frontend/src/features/checklist/ChecklistView.tsx
frontend/src/features/checklist/__tests__/ChecklistItems.test.tsx
frontend/src/features/checklist/__tests__/FuelLevel.test.tsx
frontend/src/features/checklist/__tests__/ChecklistView.test.tsx
frontend/src/routes.tsx

### Review Findings

> Code review executado em 2026-04-23 — 2 decision-needed, 12 patches, 3 deferred, 1 dismissed.

#### Decisões necessárias

- [x] [Review][Decision → Patch] Timezone: frontend converte `datetime-local` para ISO UTC com `new Date(value).toISOString()` antes de enviar
- [x] [Review][Decision → Patch] PATCH em devolvido: adicionar guarda `if checklist.status != ChecklistStatus.entregue → ChecklistError 400` em `update_entrega`

#### Patches

- [x] [Review][Patch] `GET /api/v1/checklists/{id}` não existe — `ChecklistView` chama esse endpoint mas só existe `GET /checklists` (lista) [backend/app/api/routes/checklists.py]
- [x] [Review][Patch] Backend aceita `itens` com qualquer comprimento e `status: null` — sem validação de 20 itens obrigatórios no schema/service [backend/app/schemas/checklist.py, services/checklist_service.py]
- [x] [Review][Patch] `useForm` `defaultValues` congelados no mount antes de `checklist` carregar — formulário nunca pré-populado com dados existentes; precisa de `useEffect` + `reset(values)` [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Read-only view exibe "Não OK" quando `item.status` é `null` — condição `status === "ok" ? "OK" : "Não OK"` trata null como negativo [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] AC-1 violado na view locked — modo read-only renderiza `<ul>` sem colunas; spec exige duas colunas ("Documentação/Equipamentos" / "Condições do Veículo") também na visualização [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Erro de rede mascarado como "Checklist não encontrado" — `isError` não é verificado separadamente do `!checklist` [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] `FuelLevel` usa `role="status"` para erro de validação — deveria ser `role="alert"` (assertivo) como todos os demais campos [frontend/src/features/checklist/FuelLevel.tsx:36]
- [x] [Review][Patch] Radio inputs sem atributo `name` no DOM — exclusividade funciona via react-hook-form mas navegação por teclado entre opções do mesmo grupo quebrada nativamente [frontend/src/features/checklist/ChecklistItems.tsx]
- [x] [Review][Patch] `ChecklistResponse.nivel_combustivel` tipado como `str | None` sem validação de saída — deveria ser `Literal["1/4","2/4","3/4","4/4"] | None` no schema de resposta [backend/app/schemas/checklist.py]
- [x] [Review][Patch] `id` de `useParams` sem guarda para `undefined` — `GET /v1/checklists/undefined` pode ser disparado [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] `z.string().min(1)` para `data_entrega` aceita strings não-datetime — substituir por `z.string().refine(v => !isNaN(new Date(v).getTime()), ...)` [frontend/src/features/checklist/checklistSchema.ts]
- [x] [Review][Patch] Testes backend sem cobertura de payload incompleto (<20 itens) e `status: null` [backend/tests/api/test_checklists.py]
- [x] [Review][Patch] Frontend converte `datetime-local` para ISO UTC antes de enviar: `new Date(value).toISOString()` [frontend/src/features/checklist/ChecklistView.tsx]
- [x] [Review][Patch] Service: rejeitar PATCH em checklist `devolvido` — guarda `status != entregue → ChecklistError 400` [backend/app/services/checklist_service.py]

#### Deferidos

- [x] [Review][Defer] Concurrent PATCH causa last-write-wins silencioso — deferred, requer campo `version`/`updated_at` para controle de concorrência otimística; escopo de Story 5.1+
- [x] [Review][Defer] `update_entrega` não faz transição de `status`; `is_locked` nunca setado por nenhum endpoint — deferred, mecanismo de lock implementado em Story 5.1
- [x] [Review][Defer] MSG-012 hardcoded como "entrega" sem placeholder para "devolução" — deferred explicitamente para Story 5.1 conforme Dev Notes
