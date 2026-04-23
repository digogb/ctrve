# Story 3.2: Registrar Avarias no Mapa do Veículo

Status: done

## Story

Como Responsável,
quero marcar no mapa gráfico do veículo os locais onde existem avarias e classificá-las por tipo,
para que o estado físico do veículo na entrega fique documentado visualmente.

## Acceptance Criteria

1. Mapa SVG exibe 4 vistas do veículo: topo, lateral esquerda, lateral direita, frontal/traseira.
2. Permite marcar múltiplos pontos de avaria via onClick em qualquer vista.
3. Cada ponto marcado exige seleção do tipo: Risco, Amassado ou Trincado. Sem tipo selecionado → MSG-013.
4. Permite remover ponto de avaria marcado por engano.
5. Mapa de avarias é opcional (veículo sem avarias é válido) e **não** é exibido no checklist de devolução (RN-014).
6. Endpoint `PATCH /api/v1/checklists/{id}/entrega` aceita `avarias` como campo opcional; persiste como JSON.

## Tasks / Subtasks

- [x] **T1 — Estender modelo `Checklist` com campo `avarias` (AC: 6)**
  - [x] Em `backend/app/models/checklist.py`: adicionar `avarias: list[Any] | None = Field(default=None, sa_column=Column(JSON))`
  - [x] Campo segue mesmo padrão de `itens` (JSON column)

- [x] **T2 — Schema backend para avarias (AC: 3, 6)**
  - [x] Criar `backend/app/schemas/damage.py` com `DamagePointData(BaseModel)`: `x: float`, `y: float`, `vista: Literal["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"]`, `tipo: Literal["risco", "amassado", "trincado"]`
  - [x] Em `backend/app/schemas/checklist.py`: adicionar campo `avarias: list[DamagePointData] | None = None` em `ChecklistEntregaUpdate`
  - [x] Em `backend/app/schemas/checklist.py`: adicionar campo `avarias: list[DamagePointData] | None = None` em `ChecklistResponse`
  - [x] Import `DamagePointData` de `app.schemas.damage`

- [x] **T3 — Atualizar service `update_entrega` (AC: 6)**
  - [x] Em `backend/app/services/checklist_service.py`: persistir avarias quando presente no payload
  - [x] `if data.avarias is not None: checklist.avarias = [p.model_dump() for p in data.avarias]`
  - [x] `avarias` é opcional — se omitido no PATCH, campo não é alterado

- [x] **T4 — Testes backend (AC: 6)**
  - [x] `test_update_entrega_com_avarias`: PATCH com avarias (2+ pontos) → 200 + avarias persistidas
  - [x] `test_update_entrega_sem_avarias`: PATCH sem campo avarias → 200 + campo avarias inalterado
  - [x] `test_update_entrega_avaria_sem_tipo`: ponto com tipo inválido → 422
  - [x] `test_update_entrega_avaria_vista_invalida`: vista fora do enum → 422
  - [x] `test_get_checklist_retorna_avarias`: GET /{id} retorna avarias no response

- [x] **T5 — Tipos TypeScript (AC: 1–5)**
  - [x] Criar `frontend/src/types/damage.ts`:
    - `TipoAvaria = "risco" | "amassado" | "trincado"`
    - `VistaVeiculo = "topo" | "lateral_esquerda" | "lateral_direita" | "frontal_traseira"`
    - `DamagePoint = { x: number; y: number; vista: VistaVeiculo; tipo: TipoAvaria }`
  - [x] Em `frontend/src/types/checklist.ts`: adicionar `avarias: DamagePoint[] | null` em `ChecklistResponse`
  - [x] Import `DamagePoint` de `../types/damage` (ou definir inline no mesmo arquivo se preferível)

- [x] **T6 — Schema Zod para avarias (AC: 3)**
  - [x] Em `frontend/src/features/checklist/checklistSchema.ts`: adicionar `damagePointSchema` e estender `checklistEntregaSchema` com `avarias: z.array(damagePointSchema).default([])`
  - [x] `damagePointSchema = z.object({ x: z.number(), y: z.number(), vista: z.enum([...]), tipo: z.enum(["risco", "amassado", "trincado"], { message: MSG-013 }) })`

- [x] **T7 — Componente `DamageMap.tsx` (AC: 1, 2, 3, 4)**
  - [x] Criar `frontend/src/features/damage-map/DamageMap.tsx`
  - [x] Renderiza 4 vistas SVG inline (topo, lateral esquerda, lateral direita, frontal/traseira)
  - [x] Cada vista: SVG com `viewBox` e contorno simplificado do veículo; click handler calcula coordenadas relativas (percentage-based 0–100 no viewBox)
  - [x] Ao clicar numa vista: exibe seletor de tipo inline (3 botões: Risco, Amassado, Trincado) no local clicado
  - [x] Seleção do tipo confirma o ponto → adiciona ao array via `onChange`
  - [x] Cada ponto renderizado como marcador colorido sobre o SVG (cor por tipo: vermelho=risco, laranja=amassado, azul=trincado)
  - [x] Clicar em ponto existente → botão "Remover" remove o ponto do array
  - [x] Aceita props: `value: DamagePoint[]`, `onChange: (points: DamagePoint[]) => void`, `readOnly?: boolean`
  - [x] Em `readOnly=true`: exibe pontos sem interação (sem click handlers)

- [x] **T8 — Componentes internos da feature damage-map**
  - [x] `frontend/src/features/damage-map/VehicleView.tsx` — SVG de uma vista com click handler e rendering de pontos
  - [x] `frontend/src/features/damage-map/TypeSelector.tsx` — popup/inline com 3 botões para selecionar tipo de avaria
  - [x] Cada vista SVG: contorno simplificado do veículo (retângulo com cantos arredondados + detalhes mínimos para identificação). Não precisa ser fotorrealista — apenas reconhecível

- [x] **T9 — Integrar `DamageMap` em `ChecklistView.tsx` (AC: 1, 5)**
  - [x] Modo editável: adicionar `<Controller name="avarias" control={control} render={...} />` com `DamageMap` entre `FuelLevel` e o botão Salvar
  - [x] Modo read-only (is_locked): renderizar `<DamageMap value={checklist.avarias ?? []} readOnly />` — somente se `checklist.avarias?.length > 0`
  - [x] `useEffect` reset: incluir `avarias: checklist.avarias ?? []`
  - [x] RN-014 (somente entrega): a seção DamageMap **não** deve aparecer se status for `devolvido` — adicionar guarda `checklist.status !== "devolvido"`

- [x] **T10 — Testes frontend (AC: 1–5)**
  - [x] `frontend/src/features/damage-map/__tests__/DamageMap.test.tsx`:
    - Renderiza 4 vistas SVG identificáveis
    - Click em vista → exibe seletor de tipo
    - Selecionar tipo → ponto adicionado no array (onChange chamado)
    - Click em ponto existente → opção remover → ponto removido
    - Modo readOnly: pontos exibidos, sem click handlers
  - [x] `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx`: adicionar teste para seção DamageMap visível no modo editável

## Dev Notes

### Armazenamento: JSON no Checklist (mesmo padrão de `itens`)

Arquitetura menciona `models/damage_point.py` mas o padrão estabelecido em Story 3.1 é JSON direto no `Checklist`. Adicionar `avarias` como JSON column seguindo o mesmo padrão de `itens`. Não criar tabela separada.

```python
# backend/app/models/checklist.py — campo a adicionar
avarias: list[Any] | None = Field(default=None, sa_column=Column(JSON))
```

### Schema DamagePointData (Backend)

```python
# backend/app/schemas/damage.py — NOVO arquivo
from typing import Literal
from pydantic import BaseModel

class DamagePointData(BaseModel):
    x: float
    y: float
    vista: Literal["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"]
    tipo: Literal["risco", "amassado", "trincado"]
```

```python
# backend/app/schemas/checklist.py — estender
from app.schemas.damage import DamagePointData

class ChecklistEntregaUpdate(BaseModel):
    itens: list[ChecklistItemData]
    nivel_combustivel: Literal["1/4", "2/4", "3/4", "4/4"]
    data_entrega: datetime
    avarias: list[DamagePointData] | None = None  # ← NOVO, opcional

class ChecklistResponse(BaseModel):
    ...
    avarias: list[DamagePointData] | None = None  # ← NOVO
```

### Service `update_entrega` — trecho a adicionar

```python
# backend/app/services/checklist_service.py — dentro de update_entrega
if data.avarias is not None:
    checklist.avarias = [p.model_dump() for p in data.avarias]
# se data.avarias é None (campo omitido), não altera checklist.avarias
```

### Tipos TypeScript

```typescript
// frontend/src/types/damage.ts — NOVO arquivo
export type TipoAvaria = "risco" | "amassado" | "trincado";
export type VistaVeiculo = "topo" | "lateral_esquerda" | "lateral_direita" | "frontal_traseira";

export interface DamagePoint {
  x: number;
  y: number;
  vista: VistaVeiculo;
  tipo: TipoAvaria;
}
```

```typescript
// frontend/src/types/checklist.ts — estender
import type { DamagePoint } from "./damage";

export interface ChecklistResponse {
  // ... campos existentes ...
  avarias: DamagePoint[] | null;  // ← NOVO
}
```

### Schema Zod

```typescript
// frontend/src/features/checklist/checklistSchema.ts — adicionar
import type { DamagePoint } from "../../types/damage";

export const damagePointSchema = z.object({
  x: z.number(),
  y: z.number(),
  vista: z.enum(["topo", "lateral_esquerda", "lateral_direita", "frontal_traseira"]),
  tipo: z.enum(["risco", "amassado", "trincado"], {
    message: "Selecione o tipo de avaria (Risco, Amassado ou Trincado) para cada ponto marcado no mapa do veículo.",
  }),
});

export const checklistEntregaSchema = z.object({
  itens: z.array(checklistItemSchema).length(20),
  nivel_combustivel: z.enum(["1/4", "2/4", "3/4", "4/4"], { ... }),
  data_entrega: z.string().min(1, ...).refine(...).transform(...),
  avarias: z.array(damagePointSchema).default([]),  // ← NOVO, opcional (array vazio = sem avarias)
});
```

**IMPORTANTE:** `ChecklistEntregaData` muda com a adição de `avarias` — verificar que `ChecklistView` e o `useEffect/reset` incluem o novo campo.

### DamageMap — Arquitetura do componente

```
features/damage-map/
  DamageMap.tsx          ← Componente principal: grid 2x2 com 4 vistas
  VehicleView.tsx        ← SVG de uma vista + click handler + marcadores
  TypeSelector.tsx       ← Popup inline para selecionar tipo de avaria
  __tests__/
    DamageMap.test.tsx   ← Testes da feature
```

**Props do DamageMap:**
```typescript
interface DamageMapProps {
  value: DamagePoint[];
  onChange: (points: DamagePoint[]) => void;
  readOnly?: boolean;
}
```

**Props do VehicleView:**
```typescript
interface VehicleViewProps {
  vista: VistaVeiculo;
  label: string;
  points: DamagePoint[];              // pontos desta vista apenas
  onAddPoint: (x: number, y: number) => void;
  onRemovePoint: (index: number) => void;
  readOnly?: boolean;
}
```

### SVGs — Contornos Simplificados do Veículo

Cada vista é um SVG inline com `viewBox="0 0 300 200"` (ou similar). NÃO usar imagens externas, NÃO usar bibliotecas de SVG. Desenhar contornos minimalistas com `<rect>`, `<ellipse>`, `<path>`:

- **Topo:** Retângulo com cantos arredondados (silhueta vista de cima) + indicação frente/traseira
- **Lateral esquerda:** Perfil do carro (capô, teto, porta, roda dianteira/traseira)
- **Lateral direita:** Espelhamento horizontal da lateral esquerda
- **Frontal/Traseira:** Vista frontal (grade, faróis, para-brisa)

Os SVGs devem ser simples o suficiente para serem desenhados com paths SVG básicos. O objetivo é permitir ao usuário clicar em uma posição e marcar avarias — não é necessário ser uma representação detalhada do veículo.

### Coordenadas dos pontos

Usar coordenadas relativas (percentual 0–100) em relação ao viewBox da vista:
```typescript
const handleClick = (e: React.MouseEvent<SVGSVGElement>) => {
  const svg = e.currentTarget;
  const rect = svg.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 100;
  const y = ((e.clientY - rect.top) / rect.height) * 100;
  onAddPoint(x, y);
};
```

Marcadores renderizados como `<circle>` no SVG na posição correspondente.

### Cores dos marcadores por tipo

| Tipo | Cor | CSS class |
|------|-----|-----------|
| Risco | `#EF4444` (vermelho) | `damage-risco` |
| Amassado | `#F97316` (laranja) | `damage-amassado` |
| Trincado | `#3B82F6` (azul) | `damage-trincado` |

### TypeSelector — Fluxo de interação

1. Usuário clica em área da vista SVG → cria "ponto pendente" (x, y, vista) com `tipo = null`
2. TypeSelector aparece inline próximo ao ponto clicado (posição absoluta sobre o SVG)
3. 3 botões: "Risco", "Amassado", "Trincado" + botão "Cancelar"
4. Seleção do tipo → confirma o ponto → adiciona ao array → TypeSelector some
5. Cancelar → remove ponto pendente → TypeSelector some
6. Click fora do TypeSelector → equivalente a Cancelar

### Integração em ChecklistView.tsx

```tsx
// Modo editável (dentro do <form>)
<Controller
  name="avarias"
  control={control}
  render={({ field }) => (
    <DamageMap
      value={field.value}
      onChange={field.onChange}
    />
  )}
/>

// Modo read-only (dentro do bloco is_locked)
{checklist.status !== "devolvido" && checklist.avarias && checklist.avarias.length > 0 && (
  <DamageMap value={checklist.avarias} readOnly />
)}
```

**RN-014:** Seção DamageMap NÃO aparece se `checklist.status === "devolvido"`. Atualmente não há devolução implementada, mas a guarda deve ser colocada agora.

### useEffect/reset — incluir avarias

```tsx
useEffect(() => {
  if (checklist) {
    reset({
      itens: CHECKLIST_ITEMS.map((item) => ({
        nome: item.nome,
        status: checklist.itens?.find((i) => i.nome === item.nome)?.status ?? undefined,
      })),
      nivel_combustivel: checklist.nivel_combustivel ?? undefined,
      data_entrega: checklist.data_entrega ? checklist.data_entrega.slice(0, 16) : "",
      avarias: checklist.avarias ?? [],  // ← NOVO
    });
  }
}, [checklist, reset]);
```

### defaultValues — incluir avarias

```tsx
const { control, register, reset, formState: { errors } } = useForm<ChecklistEntregaData>({
  resolver: zodResolver(checklistEntregaSchema),
  defaultValues: {
    itens: CHECKLIST_ITEMS.map((item) => ({ nome: item.nome, status: undefined })),
    nivel_combustivel: undefined,
    data_entrega: "",
    avarias: [],  // ← NOVO
  },
});
```

### Dependências e Reutilização

| Item | Localização | Uso |
|------|-------------|-----|
| `Checklist` model | `backend/app/models/checklist.py` | Estender com `avarias` JSON column |
| `ChecklistEntregaUpdate` | `backend/app/schemas/checklist.py` | Estender com `avarias` opcional |
| `ChecklistResponse` | `backend/app/schemas/checklist.py` | Estender com `avarias` |
| `update_entrega` service | `backend/app/services/checklist_service.py` | Adicionar persistência de avarias |
| `get_checklist_by_id` service | `backend/app/services/checklist_service.py` | Já retorna checklist com todos os campos |
| `checklistEntregaSchema` | `frontend/src/features/checklist/checklistSchema.ts` | Estender com `avarias` array |
| `ChecklistView.tsx` | `frontend/src/features/checklist/ChecklistView.tsx` | Integrar DamageMap via Controller |
| `ChecklistResponse` type | `frontend/src/types/checklist.ts` | Estender com `avarias` |
| `apiClient` | `frontend/src/lib/apiClient.ts` | Reutilizar, sem alteração |
| FuelLevel / ChecklistItems | `frontend/src/features/checklist/` | Padrão de referência para Controller integration |

### Anti-padrões (PROIBIDO)

- ❌ Criar tabela `damage_points` separada — usar JSON em `Checklist.avarias`
- ❌ Usar imagens externas para os SVGs — inline SVG components
- ❌ Instalar bibliotecas de SVG/canvas (react-konva, d3, etc.) — SVG inline puro com React handlers
- ❌ `any` em TypeScript
- ❌ `fetch()` direto — usar `apiClient`
- ❌ Estado com `useState` para a lista de avarias — usar `Controller` do react-hook-form
- ❌ Exibir DamageMap no checklist de devolução (RN-014)
- ❌ Alterar o comportamento do botão Salvar (permanece disabled até Story 5.1)

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 3.2 |
|-------------|--------------|----------------|
| Controller com react-hook-form para componentes customizados | Story 3.1 (ChecklistItems, FuelLevel) | Usar Controller para DamageMap no form |
| `role="alert"` para erros de validação, não `role="status"` | Story 3.1 code review | Aplicar em erros de validação da DamageMap (MSG-013) |
| `name` attribute nos radio inputs para navegação por teclado | Story 3.1 code review | Aplicar nos botões de TypeSelector |
| `useEffect` + `reset` para pré-popular form com dados do servidor | Story 3.1 code review | Incluir `avarias` no reset |
| `isAxiosError` importado de `apiClient.ts` | Story 1.1 review | Usar se necessário em error handling |
| Coordenadas relativas para posicionamento cross-browser | Arquitetura | Percentual 0–100 no viewBox |

### Estrutura de Arquivos

```
backend/app/
  models/checklist.py              ← MODIFICAR (adicionar avarias JSON column)
  schemas/damage.py                ← CRIAR (DamagePointData)
  schemas/checklist.py             ← MODIFICAR (avarias em EntregaUpdate e Response)
  services/checklist_service.py    ← MODIFICAR (persistir avarias em update_entrega)
backend/tests/
  api/test_checklists.py           ← MODIFICAR (5 novos testes T4)

frontend/src/
  types/damage.ts                                    ← CRIAR (DamagePoint, TipoAvaria, VistaVeiculo)
  types/checklist.ts                                 ← MODIFICAR (avarias no ChecklistResponse)
  features/checklist/
    checklistSchema.ts                               ← MODIFICAR (damagePointSchema, estender entregaSchema)
    ChecklistView.tsx                                ← MODIFICAR (integrar DamageMap)
  features/damage-map/                               ← CRIAR diretório
    DamageMap.tsx                                     ← CRIAR
    VehicleView.tsx                                   ← CRIAR
    TypeSelector.tsx                                  ← CRIAR
    __tests__/
      DamageMap.test.tsx                              ← CRIAR
```

### Referências

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-013, RN-014
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-013: "Selecione o tipo de avaria (Risco, Amassado ou Trincado) para cada ponto marcado no mapa do veículo."
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — "Arquitetura de Dados" (JSON), "Mapa de avarias: SVG inline com 4 vistas", "features/damage-map/"
- Story 3.1: `_bmad-output/implementation-artifacts/3-1-preencher-checklist-de-entrega.md` — padrão JSON column, Controller integration, ChecklistView structure
- Story 2.2: `_bmad-output/implementation-artifacts/2-2-buscar-checklist-por-placa.md` — padrão GET /{id}

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nenhum problema encontrado durante a implementação.

### Completion Notes List

- T1: Campo `avarias` (JSON column) adicionado ao modelo `Checklist`, seguindo padrão de `itens`
- T2: Schema `DamagePointData` criado; `ChecklistEntregaUpdate` e `ChecklistResponse` estendidos com campo `avarias`
- T3: Service `update_entrega` atualizado para persistir avarias quando presente no payload (campo opcional)
- T4: 5 testes backend adicionados: PATCH com avarias, sem avarias, tipo inválido (422), vista inválida (422), GET retorna avarias
- T5: Tipos TypeScript `TipoAvaria`, `VistaVeiculo`, `DamagePoint` criados; `ChecklistResponse` estendido
- T6: Schema Zod `damagePointSchema` criado; `checklistEntregaSchema` estendido com `avarias` array
- T7: Componente `DamageMap.tsx` implementado com grid 2x2 para 4 vistas SVG
- T8: `VehicleView.tsx` (SVG inline com contornos simplificados + marcadores coloridos) e `TypeSelector.tsx` (popup com 3 botões de tipo + cancelar) implementados
- T9: DamageMap integrado em `ChecklistView.tsx` via Controller (editável) e readOnly (locked), com guarda RN-014 (status devolvido), useEffect/reset e defaultValues atualizados
- T10: 7 testes DamageMap (4 vistas, click→seletor, tipo→ponto adicionado, remover ponto, readOnly, cancelar, múltiplas vistas) + 3 testes ChecklistView (DamageMap editável, readOnly com avarias, sem avarias)

### Change Log

- 2026-04-23: Implementação completa da Story 3.2 — Mapa de Avarias (AC 1-6)

### File List

**Novos:**
- backend/app/schemas/damage.py
- frontend/src/types/damage.ts
- frontend/src/features/damage-map/DamageMap.tsx
- frontend/src/features/damage-map/VehicleView.tsx
- frontend/src/features/damage-map/TypeSelector.tsx
- frontend/src/features/damage-map/__tests__/DamageMap.test.tsx

**Modificados:**
- backend/app/models/checklist.py
- backend/app/schemas/checklist.py
- backend/app/services/checklist_service.py
- backend/tests/api/test_checklists.py
- frontend/src/types/checklist.ts
- frontend/src/features/checklist/checklistSchema.ts
- frontend/src/features/checklist/ChecklistView.tsx
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx

### Review Findings

> Code review executado em 2026-04-23 — 2 decision-needed, 8 patches, 3 deferred, 10 dismissed.

#### Decisões necessárias

- [x] [Review][Decision → Defer] Avarias invisíveis quando status é `devolvido` — decidir quando implementar Story 4.x (devolução) se avarias da entrega devem ser visíveis read-only
- [x] [Review][Decision → Defer] Semântica `avarias: []` vs `avarias: null` apaga dados — resolver na Story 5.1 quando o botão Salvar for habilitado; enquanto Save está disabled, não há risco

#### Patches

- [x] [Review][Patch] Backend e frontend aceitam x/y fora do range 0–100 (incluindo negativos, Infinity, NaN) — adicionado `Field(ge=0, le=100)` no `DamagePointData` e `.min(0).max(100)` no Zod
- [x] [Review][Patch] Sem limite máximo de pontos de avaria — adicionado `Field(default=None, max_length=50)` na lista de avarias
- [x] [Review][Patch] SVG viewBox `0 0 300 270` corta conteúdo do TopView — viewBox ajustado para `0 0 300 300`, cy corrigido para `(point.y / 100) * 300`
- [x] [Review][Patch] `selectedIndex` fica stale quando `points` muda externamente — adicionado `useEffect(() => setSelectedIndex(null), [points.length])`
- [x] [Review][Patch] TypeSelector e botão Remover posicionados com percentuais relativos ao container — reestruturado DOM: h3 fora do container posicionado, SVG+popups em div própria com `position: relative`
- [x] [Review][Patch][Skipped] Backend retorna 422 genérico do Pydantic para tipo inválido em vez de MSG-013 — Pydantic v2 `Literal` validation executa antes de `@field_validator`, impossibilitando customização simples. Validação funciona corretamente (422 para tipo inválido); MSG-013 é enforced no frontend via Zod.
- [x] [Review][Patch] TypeSelector click-outside usa `mousedown` que não dispara em touch — trocado para `pointerdown`
- [x] [Review][Patch] Lacunas de teste: adicionados 3 testes — `avarias: []` válido, x/y fora de range → 422, campo `tipo` ausente → 422

#### Deferidos

- [x] [Review][Defer] Touch/mobile: SVG click handler usa apenas MouseEvent sem `onTouchStart`/`onPointerDown` — cross-cutting UX concern; avaliar junto com estratégia de responsividade mobile do projeto
- [x] [Review][Defer] Acessibilidade: pontos de avaria no SVG sem `tabIndex`, `role="button"`, `aria-label` ou `onKeyDown` — cross-cutting a11y; tratar em story dedicada de acessibilidade
- [x] [Review][Defer] `readOnly` DamageMap requer prop `onChange` obrigatória (noop `() => {}`) — code smell; refatorar para discriminated union quando interface evoluir
