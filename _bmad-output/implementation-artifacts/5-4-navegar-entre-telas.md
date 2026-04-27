# Story 5.4: Navegar entre Telas

Status: done

## Story

Como Responsável ou Motorista,
quero voltar à tela anterior sem perder o contexto,
para que eu possa navegar pelo sistema de forma fluida.

## Acceptance Criteria

1. Botão "Voltar" visível em todas as telas de `ChecklistView` (preenchendo entrega, preenchendo devolução, modo read-only).
2. Ao clicar em "Voltar" com dados não salvos no formulário de entrega, sistema exibe MSG-021: "Existem dados não salvos neste formulário. Deseja sair sem salvar?"
3. Se confirmado (MSG-021), navega para a tela anterior (`navigate(-1)`).
4. Se negado, formulário mantido com dados preservados — sem rerender ou reset.
5. Ao clicar em "Voltar" quando o formulário de entrega está limpo (sem alterações desde o carregamento), navega diretamente sem MSG-021.
6. Mesmo comportamento (AC 2-5) para o formulário de devolução quando não salvo.
7. Ao clicar em "Voltar" em modo read-only (checklist totalmente salvo), navega diretamente sem alerta.
8. Quando há dados não salvos, tentativa de fechar/atualizar a aba do browser aciona o diálogo nativo do browser (`window.onbeforeunload`).
9. Hook `useUnsavedChanges(isDirty: boolean)` criado em `frontend/src/hooks/useUnsavedChanges.ts` — exporta `guardedNavigate(to: string | number)`.
10. Testes: botão "Voltar" visível, form sujo → MSG-021 exibido, confirm → navega, deny → permanece, form limpo → navega direto, read-only → navega direto.

## Tasks / Subtasks

- [x] **T1 — Hook useUnsavedChanges (AC: 2-9)**
  - [x] T1.1: Criar `frontend/src/hooks/useUnsavedChanges.ts`
  - [x] T1.2: Importar `useNavigate` de `react-router-dom` e `useCallback`, `useEffect` de `react`
  - [x] T1.3: Parâmetro `isDirty: boolean` → retornar `{ guardedNavigate }`
  - [x] T1.4: `useEffect` para adicionar/remover listener `beforeunload` quando `isDirty` é `true`
  - [x] T1.5: `guardedNavigate(to)`: se `isDirty && !window.confirm(MSG_021)` → return; senão `navigate` com tipo correto

- [x] **T2 — ChecklistView: botão Voltar + wiring (AC: 1-8, 10)**
  - [x] T2.1: Importar `useUnsavedChanges` de `../../hooks/useUnsavedChanges`
  - [x] T2.2: Adicionar `devolucaoDirty` state: `const [devolucaoDirty, setDevolucaoDirty] = useState(false)`
  - [x] T2.3: Calcular flags dirty antes dos early returns usando `checklist?.is_locked` e `checklist?.status`
  - [x] T2.4: Chamar hook `useUnsavedChanges(isFormDirtyEntrega || isFormDirtyDevolucao)` antes dos early returns
  - [x] T2.5: Botão "← Voltar" adicionado antes do `<h1>` com `onClick={() => guardedNavigate(-1)}`
  - [x] T2.6: `onDirtyChange={setDevolucaoDirty}` passado ao `<DevolucaoForm>`

- [x] **T3 — DevolucaoForm: expor isDirty via prop (AC: 6)**
  - [x] T3.1: Prop `onDirtyChange?: (dirty: boolean) => void` adicionada
  - [x] T3.2: `isDirty` extraído junto com `errors` e `isSubmitting` em `formState`
  - [x] T3.3: `useEffect(() => { onDirtyChange?.(isDirty); }, [isDirty, onDirtyChange])`

- [x] **T4 — Testes (AC: 1, 2, 4, 5, 7, 10)**
  - [x] T4.1: Testado via `window.confirm` spy (comportamento real, sem mock do hook)
  - [x] T4.2: Botão "Voltar" visível quando `is_locked: false`
  - [x] T4.3: Botão "Voltar" visível quando read-only (`status: "devolvido"`)
  - [x] T4.4: Form limpo → clicar Voltar → `window.confirm` NÃO chamado
  - [x] T4.5: Form sujo → clicar Voltar → `window.confirm` chamado com MSG-021
  - [x] T4.6: `window.confirm` → `true` → navega para tela anterior (`renderAtWithHistory`)
  - [x] T4.7: `window.confirm` → `false` → botão Voltar ainda no DOM

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `useNavigate` de react-router-dom | `react-router-dom` v7.14.2 | Disponível — importar no hook |
| `entregaForm.formState.isDirty` | `ChecklistView.tsx` — `entregaForm` via `useForm` | Disponível via `entregaForm.formState` |
| `DevolucaoForm` component | `ChecklistView.tsx` linhas 147-307 | Existente — adicionar prop `onDirtyChange` |
| `Button` component (shadcn) | `components/ui/button.tsx` | Pronto — usar com `variant="ghost"` |
| `useState`, `useEffect`, `useCallback` | react | Disponíveis |
| `window.confirm` pattern | `ChecklistView.tsx:201,360` | Padrão estabelecido na codebase |
| `vi.spyOn(window, "confirm")` | `ChecklistView.test.tsx` (stories 5.1, 5.3) | Padrão de teste estabelecido |
| `hooks/` directory | `frontend/src/hooks/` | Diretório já existe (vazio) |

### O que NÃO usar

| Item | Motivo |
|------|--------|
| `useBlocker` de react-router-dom | **REQUER DATA ROUTER** — lança erro com `BrowserRouter`. Linha 7467 do chunk: `useDataRouterContext("useBlocker")`. O projeto usa `<BrowserRouter>` em `App.tsx`, não `createBrowserRouter`. |
| `unstable_usePrompt` de react-router-dom | Wrapper de `useBlocker` — mesmo problema |
| `ConfirmDialog.tsx` | Fora do escopo — `window.confirm` é o padrão atual |
| `navigate("/")` no Voltar | Deve ser `navigate(-1)` — "retorna à tela anterior" (história do browser) |

### O que falta (escopo desta story)

1. **Novo arquivo**: `frontend/src/hooks/useUnsavedChanges.ts` (20-30 linhas)
2. **ChecklistView.tsx**: botão Voltar + import do hook + `devolucaoDirty` state + `isAnyFormDirty` + prop para DevolucaoForm
3. **DevolucaoForm** (dentro de ChecklistView.tsx): adicionar prop `onDirtyChange` + `useEffect` que notifica pai
4. **ChecklistView.test.tsx**: adicionar ~7 testes

### Padrão de referência — useUnsavedChanges.ts

```typescript
import { useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const MSG_021 =
  "Existem dados não salvos neste formulário. Deseja sair sem salvar?";

export function useUnsavedChanges(isDirty: boolean) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isDirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isDirty]);

  const guardedNavigate = useCallback(
    (to: string | number) => {
      if (isDirty && !window.confirm(MSG_021)) return;
      if (typeof to === "number") navigate(to);
      else navigate(to);
    },
    [isDirty, navigate]
  );

  return { guardedNavigate };
}
```

**NOTA TypeScript**: `navigate` aceita overloads `(to: To)` e `(delta: number)`. O `if typeof to === "number"` separa os casos corretamente sem type assertions.

### Padrão de referência — ChecklistView.tsx (diff das alterações)

```typescript
// Novos imports (adicionar ao import existente de react):
import { useState, useEffect, ... } from "react";
// Novo import:
import { useUnsavedChanges } from "../../hooks/useUnsavedChanges";

// Dentro do componente ChecklistView, junto com outros states/hooks:
const [devolucaoDirty, setDevolucaoDirty] = useState(false);
const isAnyFormDirty =
  (isFillingEntrega && entregaForm.formState.isDirty) ||
  (isFillingDevolucao && devolucaoDirty);
const { guardedNavigate } = useUnsavedChanges(isAnyFormDirty);

// ATENÇÃO: isFillingEntrega, isFillingDevolucao são declarados ABAIXO do return precoce.
// Mover o cálculo para DEPOIS dessas declarações (ou calcular inline na flag).
// Alternativa: usar is_locked e status diretamente:
// const isAnyFormDirty = ((!checklist?.is_locked) && entregaForm.formState.isDirty) ||
//                        ((checklist?.is_locked && checklist?.status === "entregue") && devolucaoDirty);
```

**ATENÇÃO sobre ordem**: As variáveis `isFillingEntrega` e `isFillingDevolucao` são calculadas APÓS os returns precoces (loading, error, etc.) em `ChecklistView.tsx`. O hook `useUnsavedChanges` deve ser chamado ANTES dos returns precoces (regra dos hooks React). Portanto:

```tsx
// Usar os valores do checklist diretamente para calcular a flag:
// ANTES dos returns precoces, usar checklist que pode ser undefined:
const isFormDirtyEntrega = !checklist?.is_locked && entregaForm.formState.isDirty;
const isFormDirtyDevolucao =
  checklist?.is_locked === true &&
  checklist?.status === "entregue" &&
  devolucaoDirty;
const { guardedNavigate } = useUnsavedChanges(
  isFormDirtyEntrega || isFormDirtyDevolucao
);
```

```tsx
// Botão Voltar — adicionar ANTES do <h1> na seção principal:
<div className="mx-auto max-w-4xl space-y-6 p-4">
  <Button
    type="button"
    variant="ghost"
    className="mb-2 px-0 text-sm"
    onClick={() => guardedNavigate(-1)}
  >
    ← Voltar
  </Button>
  <h1 className="text-2xl font-bold">{title}</h1>
  ...
</div>
```

```tsx
// Passar onDirtyChange para DevolucaoForm quando isFillingDevolucao:
{isFillingDevolucao && (
  <DevolucaoForm checklist={checklist} onDirtyChange={setDevolucaoDirty} />
)}
```

### Padrão de referência — DevolucaoForm (alteração mínima)

```typescript
function DevolucaoForm({
  checklist,
  onDirtyChange,
}: {
  checklist: ChecklistResponse;
  onDirtyChange?: (dirty: boolean) => void;
}) {
  // ... código existente ...
  const { control, register, reset, handleSubmit, setError, formState: { errors, isSubmitting, isDirty } } = useForm<...>({...});

  // Adicionar:
  useEffect(() => {
    onDirtyChange?.(isDirty);
  }, [isDirty, onDirtyChange]);

  // ... resto do código existente sem alterações ...
}
```

**NOTA**: `isDirty` já pode ser extraído junto com `errors` e `isSubmitting` na desestruturação existente do `formState`.

### Padrão de referência — Testes frontend

Adicionar ao `describe("ChecklistView")` em `ChecklistView.test.tsx`.

**Para testar form "sujo"**: após renderizar, alterar um input do formulário com `fireEvent.change`. O React Hook Form então marca `isDirty = true`.

```typescript
it("exibe botão Voltar quando não bloqueado", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST }); // is_locked: false
  renderAt("1");
  await waitFor(() => {
    expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
  });
});

it("exibe botão Voltar quando read-only", async () => {
  const devolvido: ChecklistResponse = {
    ...BASE_CHECKLIST,
    is_locked: true,
    status: "devolvido",
  };
  vi.mocked(apiClient.get).mockResolvedValue({ data: devolvido });
  renderAt("1");
  await waitFor(() => {
    expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
  });
});

it("Voltar sem alterações não exibe confirm", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
  const confirmSpy = vi.spyOn(window, "confirm");
  renderAt("1");

  await waitFor(() => screen.getByRole("button", { name: /voltar/i }));
  fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

  expect(confirmSpy).not.toHaveBeenCalled();
});

it("Voltar com form sujo exibe MSG-021", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
  vi.spyOn(window, "confirm").mockReturnValueOnce(false);
  renderAt("1");

  await waitFor(() => screen.getByLabelText(/data e horário/i));
  // Tornar form dirty:
  fireEvent.change(screen.getByLabelText(/data e horário/i), {
    target: { value: "2026-04-27T10:00" },
  });

  fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

  expect(window.confirm).toHaveBeenCalledWith(
    "Existem dados não salvos neste formulário. Deseja sair sem salvar?"
  );
});

it("Voltar com negação permanece na tela", async () => {
  vi.mocked(apiClient.get).mockResolvedValue({ data: BASE_CHECKLIST });
  vi.spyOn(window, "confirm").mockReturnValueOnce(false);
  renderAt("1");

  await waitFor(() => screen.getByLabelText(/data e horário/i));
  fireEvent.change(screen.getByLabelText(/data e horário/i), {
    target: { value: "2026-04-27T10:00" },
  });
  fireEvent.click(screen.getByRole("button", { name: /voltar/i }));

  expect(screen.getByRole("button", { name: /voltar/i })).toBeInTheDocument();
});
```

**NOTA sobre `navigate(-1)` em MemoryRouter**: `navigate(-1)` em MemoryRouter sem histórico anterior não navega (histórico vazio). Para verificar que a navegação ocorreu, adicionar uma rota de entrada no `renderAt` com `initialEntries`:
```typescript
// Versão estendida para teste de navegação:
function renderAtWithHistory(id: string) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={["/", `/checklists/${id}`]} initialIndex={1}>
        <Routes>
          <Route path="/" element={<div data-testid="home">Home</div>} />
          <Route path="/checklists/:id" element={<ChecklistView />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>
  );
}
```

### Regra dos Hooks React — CRÍTICO

`useUnsavedChanges` chama `useNavigate` internamente, portanto deve ser chamado no nível do componente, NÃO dentro de um `if` ou após um return precoce. Em `ChecklistView.tsx`, os returns precoces (`if (!id)`, `if (isLoading)`, etc.) ficam ANTES de `isFillingEntrega` ser calculado. 

**Solução**: calcular `isFormDirtyEntrega` e `isFormDirtyDevolucao` usando `checklist?.is_locked` e `checklist?.status` (que podem ser `undefined`) e chamar `useUnsavedChanges` antes dos returns precoces:

```typescript
// Antes dos returns precoces (junto com isLoading, isError, etc.):
const isFormDirtyEntrega =
  checklist !== undefined &&
  !checklist.is_locked &&
  entregaForm.formState.isDirty;
const isFormDirtyDevolucao =
  checklist !== undefined &&
  checklist.is_locked === true &&
  checklist.status === "entregue" &&
  devolucaoDirty;
const { guardedNavigate } = useUnsavedChanges(
  isFormDirtyEntrega || isFormDirtyDevolucao
);
```

`devolucaoDirty` também deve ser declarado antes dos returns precoces:
```typescript
const [devolucaoDirty, setDevolucaoDirty] = useState(false);
```

### Banco de dados

Sem alteração no backend. Sem nova rota. Story 100% frontend.

### Impacto em testes existentes

Nenhum. O botão "Voltar" é adicionado ao JSX sem alterar lógica existente. `useUnsavedChanges` é um novo hook que não afeta componentes existentes. `DevolucaoForm` recebe nova prop opcional `onDirtyChange` — prop opcional não quebra código existente.

### Anti-padrões (PROIBIDO)

- `useBlocker` — requer data router, o projeto usa `BrowserRouter` (lança erro em runtime)
- `unstable_usePrompt` — mesma restrição de data router
- `navigate("/")` no botão Voltar — deve ser `navigate(-1)` (retorna à tela anterior, não ao Dashboard)
- Chamar `useUnsavedChanges` APÓS returns precoces — viola regra dos hooks React
- Criar `ConfirmDialog.tsx` — fora do escopo, `window.confirm` é o padrão atual
- Bloquear a navegação do botão "Cancelar" (Story 5.3) — o `isDirty` é verificado apenas quando `!is_locked`, e o Cancel deleta o checklist antes de navegar, então após a deleção o checklist é `undefined` e `isDirty` seria `false`

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 5.4 |
|-------------|--------------|-----------------|
| `window.confirm` para confirmações | Stories 5.1, 5.3 | MSG-021 segue mesmo padrão |
| `vi.spyOn(window, "confirm").mockReturnValueOnce(false)` | `ChecklistView.test.tsx` (story 5.3) | Mockar confirm nos testes |
| `entregaForm = useForm(...)` já declarado | `ChecklistView.tsx:325-336` | Usar `entregaForm.formState.isDirty` |
| Regra dos hooks: chamar antes de returns precoces | React docs + prática | `useUnsavedChanges` e `useState(devolucaoDirty)` devem vir antes dos ifs de loading/error |
| `Button variant="ghost"` em shadcn | `components/ui/button.tsx` | Voltar usa variant="ghost" (botão de ação secundária) |
| `useNavigate` já importado em `ChecklistForm.tsx` | story 5.3 | Mas NOT em `ChecklistView.tsx` — hook importado via `useUnsavedChanges` |
| Props opcionais com `?:` não quebram testes existentes | Padrão TypeScript | `onDirtyChange?:` em DevolucaoForm é retrocompatível |

### Sequência de Implementação Recomendada

1. T1 (hook `useUnsavedChanges`) → testar isolado: importar e verificar sem erros de build
2. T3 (DevolucaoForm prop `onDirtyChange`) → testar que prop opcional não quebra testes existentes
3. T2 (ChecklistView: botão Voltar + wiring) → testar manualmente no browser (form limpo navega, form sujo mostra diálogo)
4. T4 (testes frontend) → `npm test -- ChecklistView`

### Project Structure Notes

**Arquivos nesta story:**

| Arquivo | Tipo |
|---------|------|
| `frontend/src/hooks/useUnsavedChanges.ts` | **NOVO** |
| `frontend/src/features/checklist/ChecklistView.tsx` | Modificado — botão Voltar + hook + `devolucaoDirty` state |
| `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx` | Modificado — 5-7 novos testes |

**Nenhuma alteração no backend.** Nenhum arquivo de teste novo — adicionar ao test file existente.

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-025
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-021
- User story: `_bmad-output/requirements/user-stories.md` — US-014
- Arquitetura: `_bmad-output/planning-artifacts/architecture.md` — US-014 → `hooks/useUnsavedChanges.ts`
- Epics: `_bmad-output/planning-artifacts/epics.md` — Story 5.4
- Story anterior: `_bmad-output/implementation-artifacts/5-3-cancelar-checklist.md` — padrões de navigate, window.confirm, botões em ChecklistView
- Deferred work: `_bmad-output/implementation-artifacts/deferred-work.md` — nenhum item diretamente aplicável
- React Router v7 `useBlocker` source: `node_modules/react-router/dist/development/chunk-ZZNWZ5Q3.js:7467` — confirma requisito de data router (NÃO usar)

## Review Findings

#### Decision Needed

_(nenhuma)_

#### Patches

- [x] [Review][Patch] `beforeunload` handler — `e.returnValue = ''` adicionado; AC-8 agora funciona em Chrome/Edge/Safari. [frontend/src/hooks/useUnsavedChanges.ts]
- [x] [Review][Patch] Teste AC-1 `isFillingDevolucao` adicionado — "exibe botão Voltar quando checklist está preenchendo devolução". [frontend/src/features/checklist/__tests__/ChecklistView.test.tsx]
- [x] [Review][Patch] Teste AC-6 devolução dirty adicionado — "Voltar com form devolução sujo exibe MSG-021". [frontend/src/features/checklist/__tests__/ChecklistView.test.tsx]
- [x] [Review][Patch] "Voltar sem alterações" — refatorado com history setup; asserta navegação para home sem confirm. [frontend/src/features/checklist/__tests__/ChecklistView.test.tsx]
- [x] [Review][Patch] "Voltar com negação" — renomeado e refatorado com history setup; asserta `queryByTestId("home")` não no DOM. [frontend/src/features/checklist/__tests__/ChecklistView.test.tsx]

#### Deferred

- [x] [Review][Defer] `guardedNavigate` type narrowing é dead code — ambos os branches chamam `navigate(to)` identicamente; usar `navigate(to)` diretamente em refactor. [frontend/src/hooks/useUnsavedChanges.ts] — deferred
- [x] [Review][Defer] `devolucaoDirty` state stale após unmount de `DevolucaoForm` — self-correcting via `isFormDirtyDevolucao` no fluxo normal; tratar se cenário de remount aparecer. [frontend/src/features/checklist/ChecklistView.tsx] — deferred
- [x] [Review][Defer] `navigate(-1)` no-op em stack de histórico vazio — comportamento padrão do React Router; adicionar feedback ao usuário se necessário. [frontend/src/hooks/useUnsavedChanges.ts] — deferred
- [x] [Review][Defer] `isFormDirtyDevolucao` recalcula condições já garantidas pelo guard de render — manutenção, não bug; refatorar junto com DevolucaoForm se necessário. [frontend/src/features/checklist/ChecklistView.tsx] — deferred
- [x] [Review][Defer] `useUnsavedChanges` acoplado ao React Router — `navigate` poderia ser parâmetro para melhor testabilidade. [frontend/src/hooks/useUnsavedChanges.ts] — deferred
- [x] [Review][Defer] `MSG_021` não exportada — string duplicada entre implementação e testes; exportar quando necessário. [frontend/src/hooks/useUnsavedChanges.ts] — deferred
- [x] [Review][Defer] Churn de event listener durante loading — hooks chamados incondicionalmente por design do React; impacto negligenciável. [frontend/src/features/checklist/ChecklistView.tsx] — deferred

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6 — 2026-04-27

### Completion Notes

- Novo arquivo `frontend/src/hooks/useUnsavedChanges.ts`: hook que recebe `isDirty: boolean`, registra `beforeunload` quando sujo, e expõe `guardedNavigate(to: string | number)` com `window.confirm(MSG_021)` como guarda.
- `useBlocker` NÃO usado — requer data router; projeto usa `BrowserRouter`. Decisão documentada na story.
- `DevolucaoForm` em `ChecklistView.tsx`: prop opcional `onDirtyChange` adicionada; `isDirty` extraído do formState; `useEffect` notifica pai quando muda.
- `ChecklistView.tsx`: `devolucaoDirty` state + `isFormDirtyEntrega`/`isFormDirtyDevolucao` calculados antes dos early returns (regra dos hooks); `guardedNavigate` do hook; botão "← Voltar" antes do `<h1>`; `onDirtyChange={setDevolucaoDirty}` passado ao DevolucaoForm.
- 6 testes novos: botão visível (entrega + read-only), form limpo sem confirm, form sujo exibe MSG-021, negação permanece, confirmação navega (via `renderAtWithHistory` com rota "/").
- Total: 108 testes frontend passando (sem regressões). Backend inalterado.

### Change Log

- 2026-04-27: Story 5.4 implementada — `useUnsavedChanges.ts` + botão Voltar em ChecklistView + `onDirtyChange` em DevolucaoForm + 6 testes.

## File List

- frontend/src/hooks/useUnsavedChanges.ts (novo)
- frontend/src/features/checklist/ChecklistView.tsx (modificado)
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx (modificado)
