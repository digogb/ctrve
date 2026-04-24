# Story 3.3: Coletar Assinaturas na Entrega

Status: done

## Story

Como Responsável,
quero coletar a assinatura digital do Responsável e do Motorista no checklist de entrega,
para que ambas as partes confirmem as condições registradas.

## Acceptance Criteria

1. Dois campos de assinatura separados: "Assinatura do Responsável" e "Assinatura do Motorista", cada um usando canvas HTML5 via `react-signature-canvas`.
2. Cada campo possui botão "Limpar" que apaga a assinatura atual e permite refazer.
3. Ambas as assinaturas são obrigatórias para salvar o checklist (MSG-014). Validação será enforced na Story 5.1 quando o botão Salvar for habilitado; nesta story, os campos são adicionados como opcionais no schema.
4. Assinaturas armazenadas como string base64 (data URL PNG) no banco. Não editáveis após `is_locked = true` (RN-016).
5. Modo read-only (`is_locked`): exibe assinaturas como `<img>` sem interação.
6. Endpoint `PATCH /api/v1/checklists/{id}/entrega` aceita `assinatura_responsavel` e `assinatura_motorista` como campos opcionais (string base64).

## Tasks / Subtasks

- [x] **T1 — Estender modelo `Checklist` com campos de assinatura (AC: 4, 6)**
  - [x] Em `backend/app/models/checklist.py`: adicionar `assinatura_responsavel: str | None = None` e `assinatura_motorista: str | None = None`
  - [x] Ambos são `str | None` (Text column — base64 de ~50-100KB)

- [x] **T2 — Estender schemas backend (AC: 6)**
  - [x] Em `backend/app/schemas/checklist.py`: adicionar em `ChecklistEntregaUpdate`:
    - `assinatura_responsavel: str | None = None`
    - `assinatura_motorista: str | None = None`
  - [x] Em `backend/app/schemas/checklist.py`: adicionar em `ChecklistResponse`:
    - `assinatura_responsavel: str | None = None`
    - `assinatura_motorista: str | None = None`
  - [x] Validação: se fornecido, o valor deve iniciar com `data:image/png;base64,` (usar `field_validator`)

- [x] **T3 — Atualizar service `update_entrega` (AC: 6)**
  - [x] Em `backend/app/services/checklist_service.py`: persistir assinaturas quando presentes no payload
  - [x] `if data.assinatura_responsavel is not None: checklist.assinatura_responsavel = data.assinatura_responsavel`
  - [x] `if data.assinatura_motorista is not None: checklist.assinatura_motorista = data.assinatura_motorista`
  - [x] Campos opcionais — se omitidos no PATCH, não alterar

- [x] **T4 — Testes backend (AC: 4, 6)**
  - [x] `test_update_entrega_com_assinaturas`: PATCH com ambas assinaturas → 200 + assinaturas persistidas
  - [x] `test_update_entrega_sem_assinaturas`: PATCH sem campos de assinatura → 200 + campos inalterados
  - [x] `test_update_entrega_assinatura_formato_invalido`: assinatura sem prefixo `data:image/png;base64,` → 422
  - [x] `test_get_checklist_retorna_assinaturas`: GET /{id} retorna assinaturas no response

- [x] **T5 — Instalar `react-signature-canvas` (AC: 1)**
  - [x] `npm install react-signature-canvas @types/react-signature-canvas`
  - [x] Verificar compatibilidade com React 19 (biblioteca é class component — deve funcionar)

- [x] **T6 — Tipos TypeScript (AC: 1, 4, 5)**
  - [x] Em `frontend/src/types/checklist.ts`: adicionar ao `ChecklistResponse`:
    - `assinatura_responsavel: string | null`
    - `assinatura_motorista: string | null`

- [x] **T7 — Schema Zod (AC: 3)**
  - [x] Em `frontend/src/features/checklist/checklistSchema.ts`: estender `checklistEntregaSchema` com:
    - `assinatura_responsavel: z.string().nullable().default(null)` (opcional por ora — Story 5.1 tornará required com MSG-014)
    - `assinatura_motorista: z.string().nullable().default(null)` (idem)

- [x] **T8 — Componente `SignaturePad.tsx` (AC: 1, 2)**
  - [x] Criar `frontend/src/features/signature/SignaturePad.tsx`
  - [x] Props: `{ value: string | null; onChange: (value: string | null) => void; label: string; readOnly?: boolean }`
  - [x] Modo editável: `react-signature-canvas` com `ref`, `penColor="#000"`, `canvasProps={{ className: "..." }}`
  - [x] Ao finalizar traço (`onEnd`): `onChange(sigCanvas.current.toDataURL("image/png"))`
  - [x] Botão "Limpar": `sigCanvas.current.clear()` + `onChange(null)`
  - [x] Se `value` muda externamente para `null` (reset do form): limpar o canvas via `useEffect`
  - [x] Modo readOnly: renderizar `<img src={value} alt={label} />` sem canvas

- [x] **T9 — Testes frontend do `SignaturePad` (AC: 1, 2, 5)**
  - [x] Criar `frontend/src/features/signature/__tests__/SignaturePad.test.tsx`
  - [x] Renderiza canvas com label
  - [x] Botão "Limpar" visível em modo editável
  - [x] Modo readOnly com value: renderiza `<img>` com src correto
  - [x] Modo readOnly sem value: não renderiza nada (ou placeholder)
  - [x] Botão "Limpar" ausente em modo readOnly

- [x] **T10 — Integrar `SignaturePad` em `ChecklistView.tsx` (AC: 1, 2, 3, 5)**
  - [x] Modo editável: dois `<Controller>` com `SignaturePad` — um para `assinatura_responsavel`, outro para `assinatura_motorista`
  - [x] Posicionar após DamageMap e antes do botão Salvar
  - [x] Modo read-only (`is_locked`): exibir assinaturas como `<SignaturePad readOnly value={checklist.assinatura_responsavel} label="Assinatura do Responsável" onChange={() => {}} />` (e idem para motorista)
  - [x] `useEffect/reset`: incluir `assinatura_responsavel` e `assinatura_motorista`
  - [x] `defaultValues`: incluir ambos como `null`

- [x] **T11 — Testes de integração ChecklistView (AC: 1, 5)**
  - [x] Em `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx`:
    - Seção de assinaturas visível no modo editável
    - Modo read-only com assinaturas: exibe imagens
    - Modo read-only sem assinaturas: não exibe seção (ou placeholder)

## Dev Notes

### Biblioteca: react-signature-canvas

Arquitetura especifica `react-signature-canvas` (wrapper sobre `signature_pad`). Versão mais recente: `1.1.0-alpha.2`. Instalar com:

```bash
cd frontend && npm install react-signature-canvas @types/react-signature-canvas
```

API principal:
- `ref.current.toDataURL("image/png")` → string base64 `data:image/png;base64,...`
- `ref.current.clear()` → limpa o canvas
- `ref.current.isEmpty()` → boolean (útil para validação futura)
- Props: `penColor`, `canvasProps`, `onEnd` (callback ao finalizar traço)

A biblioteca é class-based, compatível com React 19 (class components ainda são suportados).

### Modelo de dados — campos de assinatura

```python
# backend/app/models/checklist.py — adicionar
assinatura_responsavel: str | None = None  # base64 PNG ~50-100KB
assinatura_motorista: str | None = None     # base64 PNG ~50-100KB
```

Não usar JSON column — são strings simples. SQLite/PostgreSQL armazenam Text sem limite prático.

### Schema backend

```python
# backend/app/schemas/checklist.py — em ChecklistEntregaUpdate
from pydantic import field_validator

assinatura_responsavel: str | None = None
assinatura_motorista: str | None = None

@field_validator("assinatura_responsavel", "assinatura_motorista", mode="before")
@classmethod
def validate_base64_signature(cls, v: str | None) -> str | None:
    if v is not None and not v.startswith("data:image/png;base64,"):
        raise ValueError("Assinatura deve ser uma imagem PNG em formato base64.")
    return v
```

```python
# backend/app/schemas/checklist.py — em ChecklistResponse
assinatura_responsavel: str | None = None
assinatura_motorista: str | None = None
```

### Service — persistir assinaturas

```python
# backend/app/services/checklist_service.py — em update_entrega, após avarias
if data.assinatura_responsavel is not None:
    checklist.assinatura_responsavel = data.assinatura_responsavel
if data.assinatura_motorista is not None:
    checklist.assinatura_motorista = data.assinatura_motorista
```

### Tipos TypeScript

```typescript
// frontend/src/types/checklist.ts — adicionar ao ChecklistResponse
assinatura_responsavel: string | null;
assinatura_motorista: string | null;
```

### Schema Zod

```typescript
// frontend/src/features/checklist/checklistSchema.ts — em checklistEntregaSchema
assinatura_responsavel: z.string().nullable().default(null),
assinatura_motorista: z.string().nullable().default(null),
```

Story 5.1 mudará para:
```typescript
assinatura_responsavel: z.string().min(1, "A assinatura do Responsável é obrigatória. Assine no campo correspondente para continuar."),
assinatura_motorista: z.string().min(1, "A assinatura do Motorista é obrigatória. Assine no campo correspondente para continuar."),
```

### Componente SignaturePad

```
features/signature/
  SignaturePad.tsx          ← Componente wrapper do react-signature-canvas
  __tests__/
    SignaturePad.test.tsx   ← Testes
```

**Props:**
```typescript
interface SignaturePadProps {
  value: string | null;
  onChange: (value: string | null) => void;
  label: string;
  readOnly?: boolean;
}
```

**Implementação de referência:**
```tsx
import { useEffect, useRef } from "react";
import ReactSignatureCanvas from "react-signature-canvas";
import { Button } from "@/components/ui/button";

export default function SignaturePad({ value, onChange, label, readOnly }: SignaturePadProps) {
  const sigRef = useRef<ReactSignatureCanvas>(null);

  useEffect(() => {
    if (!readOnly && sigRef.current && !value) {
      sigRef.current.clear();
    }
  }, [value, readOnly]);

  if (readOnly) {
    if (!value) return null;
    return (
      <div>
        <p className="mb-1 text-sm font-medium">{label}</p>
        <img src={value} alt={label} className="rounded-lg border border-border" />
      </div>
    );
  }

  const handleEnd = () => {
    if (sigRef.current && !sigRef.current.isEmpty()) {
      onChange(sigRef.current.toDataURL("image/png"));
    }
  };

  const handleClear = () => {
    sigRef.current?.clear();
    onChange(null);
  };

  return (
    <div>
      <p className="mb-1 text-sm font-medium">{label}</p>
      <div className="rounded-lg border border-border">
        <ReactSignatureCanvas
          ref={sigRef}
          penColor="#000"
          canvasProps={{ className: "w-full h-40" }}
          onEnd={handleEnd}
        />
      </div>
      <Button type="button" variant="outline" size="sm" onClick={handleClear} className="mt-1">
        Limpar
      </Button>
    </div>
  );
}
```

### Integração em ChecklistView.tsx

**Modo editável (dentro do `<form>`):**
```tsx
import SignaturePad from "../signature/SignaturePad";

// Após DamageMap, antes do botão Salvar
<div className="mt-6 space-y-4">
  <h3 className="text-lg font-semibold">Assinaturas</h3>
  <Controller
    name="assinatura_responsavel"
    control={control}
    render={({ field }) => (
      <SignaturePad
        value={field.value}
        onChange={field.onChange}
        label="Assinatura do Responsável"
      />
    )}
  />
  <Controller
    name="assinatura_motorista"
    control={control}
    render={({ field }) => (
      <SignaturePad
        value={field.value}
        onChange={field.onChange}
        label="Assinatura do Motorista"
      />
    )}
  />
</div>
```

**Modo read-only (dentro do bloco `is_locked`):**
```tsx
{(checklist.assinatura_responsavel || checklist.assinatura_motorista) && (
  <div className="mt-6 space-y-4">
    <h3 className="text-lg font-semibold">Assinaturas</h3>
    <SignaturePad
      readOnly
      value={checklist.assinatura_responsavel}
      onChange={() => {}}
      label="Assinatura do Responsável"
    />
    <SignaturePad
      readOnly
      value={checklist.assinatura_motorista}
      onChange={() => {}}
      label="Assinatura do Motorista"
    />
  </div>
)}
```

**useEffect/reset:**
```tsx
useEffect(() => {
  if (checklist) {
    reset({
      // ... campos existentes ...
      assinatura_responsavel: checklist.assinatura_responsavel ?? null,
      assinatura_motorista: checklist.assinatura_motorista ?? null,
    });
  }
}, [checklist, reset]);
```

**defaultValues:**
```tsx
defaultValues: {
  // ... campos existentes ...
  assinatura_responsavel: null,
  assinatura_motorista: null,
},
```

### Testes: mock do react-signature-canvas

`react-signature-canvas` usa canvas HTML5, que não existe no jsdom. Criar mock:

```typescript
// No test file ou __mocks__
vi.mock("react-signature-canvas", () => ({
  default: vi.fn().mockImplementation(({ canvasProps, onEnd }) => (
    <canvas data-testid="signature-canvas" {...canvasProps} onClick={onEnd} />
  )),
}));
```

E para métodos do ref (`toDataURL`, `clear`, `isEmpty`):
```typescript
const mockToDataURL = vi.fn(() => "data:image/png;base64,mockdata");
const mockClear = vi.fn();
const mockIsEmpty = vi.fn(() => false);

// No mock factory, attach to ref
```

### Dependências e Reutilização

| Item | Localização | Uso |
|------|-------------|-----|
| `Checklist` model | `backend/app/models/checklist.py` | Estender com 2 campos string |
| `ChecklistEntregaUpdate` | `backend/app/schemas/checklist.py` | Estender com 2 campos string + validator |
| `ChecklistResponse` | `backend/app/schemas/checklist.py` | Estender com 2 campos string |
| `update_entrega` service | `backend/app/services/checklist_service.py` | Persistir assinaturas |
| `checklistEntregaSchema` | `frontend/src/features/checklist/checklistSchema.ts` | Estender com 2 campos nullable |
| `ChecklistView.tsx` | `frontend/src/features/checklist/ChecklistView.tsx` | Integrar SignaturePad via Controller |
| `ChecklistResponse` type | `frontend/src/types/checklist.ts` | Estender com 2 campos string |
| `apiClient` | `frontend/src/lib/apiClient.ts` | Reutilizar, sem alteração |
| shadcn `Button` | `frontend/src/components/ui/button.tsx` | Usar para botão "Limpar" |
| FuelLevel/DamageMap | `frontend/src/features/checklist/` e `damage-map/` | Padrão de referência para Controller integration |

### Anti-padrões (PROIBIDO)

- Criar tabela `signatures` separada — armazenar diretamente no `Checklist` como string
- Usar upload multipart/form-data — assinatura trafega como string base64 no JSON
- Instalar bibliotecas extras de canvas (fabric.js, konva, etc.) — usar `react-signature-canvas` conforme arquitetura
- `any` em TypeScript
- `fetch()` direto — usar `apiClient`
- Estado com `useState` para o valor da assinatura — usar `Controller` do react-hook-form
- Armazenar assinatura sem o prefixo `data:image/png;base64,` — manter o data URL completo para uso direto em `<img src>`
- Permitir edição de assinatura quando `is_locked = true`
- Alterar o comportamento do botão Salvar (permanece disabled até Story 5.1)
- Tornar assinaturas obrigatórias no Zod schema agora (será feito na Story 5.1 com MSG-014)

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 3.3 |
|-------------|--------------|----------------|
| Controller com react-hook-form para componentes customizados | Story 3.1 (ChecklistItems, FuelLevel) | Usar Controller para SignaturePad no form |
| `useEffect` + `reset` para pré-popular form com dados do servidor | Story 3.1 code review | Incluir assinaturas no reset |
| readOnly DamageMap requer prop `onChange` obrigatória (noop) | Story 3.2 review (defer) | Mesmo padrão: SignaturePad readOnly recebe `onChange={() => {}}` |
| `isAxiosError` importado de `apiClient.ts` | Story 1.1 review | Usar se necessário em error handling |
| Validação de formato no backend com `field_validator` | Padrão Pydantic v2 | Validar prefixo base64 |
| Canvas-based components precisam de mock no jsdom | Conhecimento técnico | Mock do react-signature-canvas nos testes |
| Tailwind + shadcn/ui para estilização | Migração CSS (sessão anterior) | Usar `Button variant="outline"`, `border-border`, etc. |

### Project Structure Notes

Alinhado com a estrutura do architecture.md:
```
frontend/src/features/signature/
  SignaturePad.tsx                    ← CRIAR
  __tests__/
    SignaturePad.test.tsx             ← CRIAR
```

### Estrutura de Arquivos

```
backend/app/
  models/checklist.py              ← MODIFICAR (2 campos string)
  schemas/checklist.py             ← MODIFICAR (2 campos + validator em EntregaUpdate e Response)
  services/checklist_service.py    ← MODIFICAR (persistir assinaturas em update_entrega)
backend/tests/
  api/test_checklists.py           ← MODIFICAR (4 novos testes T4)

frontend/
  package.json                     ← MODIFICAR (react-signature-canvas)
  src/
    types/checklist.ts                                 ← MODIFICAR (2 campos no ChecklistResponse)
    features/checklist/
      checklistSchema.ts                               ← MODIFICAR (2 campos nullable no schema)
      ChecklistView.tsx                                ← MODIFICAR (integrar SignaturePad)
      __tests__/ChecklistView.test.tsx                 ← MODIFICAR (testes de integração)
    features/signature/                                ← CRIAR diretório
      SignaturePad.tsx                                  ← CRIAR
      __tests__/
        SignaturePad.test.tsx                           ← CRIAR
```

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-015, RN-016
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-014: "A assinatura do {Responsável/Motorista} é obrigatória. Assine no campo correspondente para continuar."
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — "Canvas de assinatura: react-signature-canvas", "features/signature/", "Assinaturas base64 trafegam como string no JSON"
- Story 3.2: `_bmad-output/implementation-artifacts/3-2-registrar-avarias-no-mapa-do-veiculo.md` — padrão Controller integration, useEffect/reset
- Story 3.1: `_bmad-output/implementation-artifacts/3-1-preencher-checklist-de-entrega.md` — padrão form com react-hook-form
- react-signature-canvas: https://github.com/agilgur5/react-signature-canvas — API reference

### Review Findings

> Code review executado em 2026-04-23 — 1 decision-needed, 7 patches, 9 deferred, 10 dismissed.

#### Decisões necessárias

- [x] [Review][Decision → Defer] Falta migração de banco para colunas `assinatura_responsavel` e `assinatura_motorista` — em ambiente dev, deletar `ctrve.db` e deixar `create_all()` recriar; gerar Alembic migration quando deploy

#### Patches

- [x] [Review][Patch] Assinatura base64 sem limite de tamanho — adicionado `max_length=500_000` no `field_validator` do `ChecklistEntregaUpdate` [backend/app/schemas/checklist.py]
- [x] [Review][Patch] SignaturePad não restaura assinatura pré-existente no canvas — adicionado `sigRef.current.fromDataURL(value)` no `useEffect` [frontend/src/features/signature/SignaturePad.tsx]
- [x] [Review][Patch] Variáveis CSS do shadcn/ui faltando no `index.css` — adicionadas 12 variáveis (`--color-primary-foreground`, `--color-card`, etc.) [frontend/src/index.css]
- [x] [Review][Patch] Dashboard usa `<a href>` em vez de React Router `<Link>` — substituído por `<Link to="...">` [frontend/src/routes.tsx]
- [x] [Review][Patch] `RequireRole.tsx` tem `fetchMe` próprio sem tratamento de 401 — replicado tratamento retornando `null` em 401 [frontend/src/components/RequireRole.tsx]
- [x] [Review][Patch] Teste do SignaturePad não cobre cenário de `value` mudando para `null` — adicionado teste de rerender [frontend/src/features/signature/__tests__/SignaturePad.test.tsx]
- [x] [Review][Patch] Testes backend não cobrem payload de assinatura muito grande — adicionado `test_update_entrega_assinatura_muito_grande` [backend/tests/api/test_checklists.py]

#### Deferidos

- [x] [Review][Defer] Validação base64 verifica apenas prefixo, não conteúdo real — defense-in-depth, não é bug
- [x] [Review][Defer] `fetchMe` retorna `null` vs `undefined` — verificar consumers; auth fix de sessão anterior
- [x] [Review][Defer] `queryClient.cancelQueries` não awaited — race condition teórica; auth fix de sessão anterior
- [x] [Review][Defer] `session-expired` condicionado a `hadSession` — auth fix de sessão anterior
- [x] [Review][Defer] Componentes shadcn `select.tsx`, `radio-group.tsx` instalados mas não usados — para stories futuras
- [x] [Review][Defer] `react-signature-canvas` em versão alpha `1.1.0-alpha.2` — decisão arquitetural, única opção estável tem menos features
- [x] [Review][Defer] `legacy-peer-deps=true` no `.npmrc` — workaround necessário para React 19
- [x] [Review][Defer] ReadOnly mostra seção "Assinaturas" sem feedback quando uma assinatura falta — melhoria UX futura
- [x] [Review][Defer] Canvas 300x150 fixo não se redimensiona responsivamente — cross-cutting mobile UX

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

- Teste "exibe view read-only quando is_locked = true" falhava por mudança no ChecklistItems (migração shadcn removeu ":" do nome do item). Corrigido no teste.
- react-signature-canvas requer mock no jsdom (HTMLCanvasElement.getContext() não implementado). Mock adicionado no ChecklistView.test.tsx.

### Completion Notes List

- T1: Campos `assinatura_responsavel` e `assinatura_motorista` (str | None) adicionados ao modelo Checklist
- T2: Campos adicionados em ChecklistEntregaUpdate e ChecklistResponse + field_validator para prefixo `data:image/png;base64,`
- T3: Service `update_entrega` atualizado para persistir assinaturas quando presentes no payload (campos opcionais)
- T4: 4 testes backend: PATCH com assinaturas, sem assinaturas (não altera existentes), formato inválido (422), GET retorna assinaturas
- T5: react-signature-canvas 1.1.0-alpha.2 e @types/react-signature-canvas instalados
- T6: ChecklistResponse TypeScript estendido com assinatura_responsavel e assinatura_motorista
- T7: Schema Zod estendido com campos nullable (default null) — será tornado required na Story 5.1
- T8: Componente SignaturePad criado com react-signature-canvas, props value/onChange/label/readOnly, botão Limpar, modo readOnly com <img>
- T9: 7 testes SignaturePad: canvas com label, botão limpar, limpar chama onChange(null), readOnly com img, readOnly sem value (null render), limpar ausente readOnly, onEnd chama onChange
- T10: SignaturePad integrado em ChecklistView via Controller (editável) e readOnly (locked), useEffect/reset e defaultValues atualizados
- T11: 3 testes integração ChecklistView: assinaturas visíveis editável, readOnly com imagens, readOnly sem assinaturas não exibe seção
- Fix: teste read-only corrigido para nova renderização do ChecklistItems (sem ":")
- Fix: mock de react-signature-canvas adicionado no ChecklistView.test.tsx

### Change Log

- 2026-04-23: Implementação completa da Story 3.3 — Coleta de Assinaturas na Entrega (AC 1-6)

### File List

**Novos:**
- frontend/src/features/signature/SignaturePad.tsx
- frontend/src/features/signature/__tests__/SignaturePad.test.tsx

**Modificados:**
- backend/app/models/checklist.py
- backend/app/schemas/checklist.py
- backend/app/services/checklist_service.py
- backend/tests/api/test_checklists.py
- frontend/package.json
- frontend/package-lock.json
- frontend/src/types/checklist.ts
- frontend/src/features/checklist/checklistSchema.ts
- frontend/src/features/checklist/ChecklistView.tsx
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx
