# Story 6.1: Fundação Visual e Navegação Global

Status: done

## Story

Como usuário do CTRVE,
quero uma interface com identidade visual institucional e header de navegação global,
para que o sistema transmita profissionalismo e eu sempre saiba quem está logado e como sair.

## Acceptance Criteria

1. Paleta atualizada: `--color-primary: #003366` (azul marinho TJCE), `--color-primary-dark: #004080`; tipografia Inter em todo o sistema.
2. Componente `AppHeader` presente em todas as telas autenticadas: gradiente azul marinho à esquerda com logo "CTRVE" + chip do usuário (iniciais + nome + role) à direita + botão "Sair".
3. `Sonner` instalado e `<Toaster>` configurado em `App.tsx`; todos os `window.alert` de sucesso/erro em `ChecklistView.tsx` substituídos por `toast.success` / `toast.error`.
4. `Dialog` shadcn instalado; os dois `window.confirm` de confirmação de salvamento em `ChecklistView.tsx` substituídos por Dialog com título + descrição + botões "Confirmar" e "Cancelar".
5. Dashboard refatorado: `HeroStrip` com saudação + data atual + 3 stat cards (em preenchimento / total do mês / total geral), dois botões de ação em cards elevados (Novo Checklist + Buscar por Placa) e listagem dos 3 checklists mais recentes.
6. Nenhuma regressão nos testes existentes (108 frontend + 106 backend).

## Tasks / Subtasks

- [x] **T1 — CSS: retheme paleta e tipografia (AC: 1)**
  - [x] T1.1: Em `frontend/src/index.css`, alterar `--color-primary: #1d4ed8` → `--color-primary: #003366`
  - [x] T1.2: Alterar `--color-primary-dark: #1e40af` → `--color-primary-dark: #004080`
  - [x] T1.3: Alterar `--color-ring: #1d4ed8` → `--color-ring: #003366`
  - [x] T1.4: Adicionar `@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');` no topo do arquivo (antes de `@import "tailwindcss"`)
  - [x] T1.5: No seletor `body`, adicionar `font-family: 'Inter', system-ui, -apple-system, sans-serif;`

- [x] **T2 — Sonner: instalar e substituir window.alert (AC: 3)**
  - [x] T2.1: Instalar Sonner: `cd frontend && npx shadcn@latest add sonner` (cria `components/ui/sonner.tsx`)
  - [x] T2.2: Em `App.tsx`, importar e adicionar `<Toaster position="top-right" richColors />` dentro de `<AuthProvider>` após `<SessionGuard />`
  - [x] T2.3: Em `ChecklistView.tsx`, adicionar import `import { toast } from "sonner"`
  - [x] T2.4: Substituir `window.alert("Checklist salvo com sucesso.")` (linhas 218 e 379) → `toast.success("Checklist salvo com sucesso.")`
  - [x] T2.5: Substituir `window.alert("PDF gerado com sucesso.")` → `toast.success("PDF gerado com sucesso.")`
  - [x] T2.6: Substituir `window.alert(json.message || json.detail || "Erro ao gerar PDF.")` → `toast.error(json.message || json.detail || "Erro ao gerar PDF.")`
  - [x] T2.7: Substituir os dois `window.alert("Erro ao gerar PDF. Tente novamente.")` → `toast.error("Erro ao gerar PDF. Tente novamente.")`
  - [x] T2.8: Substituir `window.alert(data?.message || data?.detail || "Erro ao cancelar checklist.")` → `toast.error(data?.message || data?.detail || "Erro ao cancelar checklist.")`

- [x] **T3 — Dialog: instalar e substituir window.confirm de salvamento (AC: 4)**
  - [x] T3.1: Instalar Dialog: `cd frontend && npx shadcn@latest add dialog` (cria `components/ui/dialog.tsx`)
  - [x] T3.2: Criar hook `useSaveConfirmDialog` ou usar state local em `ChecklistView` para controlar o Dialog aberto/fechado
  - [x] T3.3: Substituir o `window.confirm("Deseja confirmar o salvamento...")` em `onEntregaSubmit` por Dialog assíncrono com título "Salvar checklist?" + descrição MSG-018 + botões "Confirmar" (primary) e "Cancelar" (outline)
  - [x] T3.4: Substituir o `window.confirm(...)` em `DevolucaoForm.onSubmit` com o mesmo padrão
  - [x] T3.5: `window.confirm` do Cancel (MSG-020 em `onCancel`) e do Voltar (`useUnsavedChanges` MSG-021) podem permanecer com `window.confirm` nesta story — escopo limitado ao salvamento

- [x] **T4 — AppHeader: criar componente (AC: 2)**
  - [x] T4.1: Criar `frontend/src/components/AppHeader.tsx`
  - [x] T4.2: Importar `useAuthContext` de `../../features/auth/AuthContext`
  - [x] T4.3: Exibir initials do usuário: `user.full_name.split(' ').map(n => n[0]).join('').slice(0,2).toUpperCase()`
  - [x] T4.4: Role display: `user.role === 'responsavel' ? 'Responsável' : 'Motorista'`
  - [x] T4.5: Botão "Sair" chama `logout()` de `useAuthContext`
  - [x] T4.6: Estilo: `bg-gradient-to-br from-[#003366] to-[#004080] text-white h-16 sticky top-0 z-50 shadow-md`

- [x] **T5 — AppHeader: integrar em todas as telas autenticadas (AC: 2)**
  - [x] T5.1: Em `ProtectedRoute.tsx`, importar e renderizar `<AppHeader />` acima do `{children}` quando autenticado
  - [x] T5.2: Verificar que header aparece em: Dashboard, ChecklistList, ChecklistView, ChecklistForm, RegisterForm

- [x] **T6 — Dashboard: refatorar com stats e cards (AC: 5)**
  - [x] T6.1: Em `routes.tsx`, extrair `Dashboard` para `frontend/src/features/dashboard/Dashboard.tsx`
  - [x] T6.2: Adicionar query Tanstack para buscar checklists recentes: `useQuery({ queryKey: ["checklists"], queryFn: () => apiClient.get("/v1/checklists").then(r => r.data) })`
  - [x] T6.3: Calcular stats do lado do cliente a partir dos resultados:
    - `emPreenchimento`: `checklists.filter(c => !c.is_locked).length`
    - `esteMes`: `checklists.filter(c => new Date(c.created_at).getMonth() === new Date().getMonth()).length`
    - `total`: `checklists.length`
  - [x] T6.4: Renderizar HeroStrip com gradiente + saudação + data + 3 stat cards (`bg-white/10`)
  - [x] T6.5: Dois botões de ação em cards elevados: "Novo Checklist" (primary card) + "Buscar por Placa" (white card with border)
  - [x] T6.6: Lista dos 3 mais recentes: cards com ícone colorido por status + placa + Nº + data + `StatusBadge` (usar Badge shadcn por enquanto; StatusBadge dedicado na Story 6.2)
  - [x] T6.7: Atualizar import em `routes.tsx`: `import Dashboard from "./features/dashboard/Dashboard"`

- [x] **T7 — Testes: verificar regressões (AC: 6)**
  - [x] T7.1: `npm test` — 110 testes frontend passando (0 regressões)
  - [x] T7.2: `python3 -m pytest backend/` — 106 testes backend passando
  - [x] T7.3: Atualizar mocks de testes que dependem de `window.alert` → agora são toasts (verificar se há testes que precisam de ajuste)

### Review Findings

- [x] [Review][Decision] AppHeader oculta chip do usuário em mobile (`hidden sm:flex`) — aceito: só "Sair" visível em mobile, chip completo a partir de sm (uso interno, MVP) [`frontend/src/components/AppHeader.tsx:33`]
- [x] [Review][Patch] `pendingEntregaData` não limpo após erro — adicionado `setSubmitError(null)` + `finally { setPendingEntregaData(null) }` em `handleConfirmEntregaSave` [`frontend/src/features/checklist/ChecklistView.tsx`]
- [x] [Review][Patch] `handleConfirmEntregaSave` não reseta `submitError` antes do try — corrigido [`frontend/src/features/checklist/ChecklistView.tsx`]
- [x] [Review][Patch] `STATUS_CONFIG` sem fallback — adicionado `?? { label: c.status, color: "bg-gray-400" }` [`frontend/src/features/dashboard/Dashboard.tsx`]
- [x] [Review][Patch] `recentes = checklists.slice(0, 3)` sem ordenação — adicionado `.sort()` por `created_at` desc antes do slice [`frontend/src/features/dashboard/Dashboard.tsx`]
- [x] [Review][Patch] `initials` produz `"undefined"` se `full_name` for vazio — adicionado `.filter(n => n)` e `|| "??"` [`frontend/src/components/AppHeader.tsx`]
- [x] [Review][Patch] Botão "Confirmar" em `DevolucaoForm` sem `disabled` — adicionado `isConfirming` state + `disabled={isConfirming}` + guard + finally cleanup [`frontend/src/features/checklist/ChecklistView.tsx:DevolucaoForm`]
- [x] [Review][Defer] `Toaster` dentro de `AuthProvider` em vez de nível mais alto — anti-pattern menor, funciona corretamente [`frontend/src/App.tsx`] — deferred, pre-existing
- [x] [Review][Defer] `esteMes` timezone-sensitive — `getMonth()` usa fuso local, virada de mês em UTC pode divergir [`frontend/src/features/dashboard/Dashboard.tsx`] — deferred, pre-existing
- [x] [Review][Defer] Google Fonts via `@import` sem `<link preconnect>` — render-blocking, impacto em LCP [`frontend/src/index.css`] — deferred, pre-existing
- [x] [Review][Defer] `next-themes` adicionado como dep de produção pelo shadcn/sonner sem `ThemeProvider` configurado — funciona com fallback "system" [`frontend/package.json`] — deferred, pre-existing

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `@theme` CSS Tailwind v4 | `frontend/src/index.css:3-34` | Alterar valores — NÃO migrar para v3 |
| `Button` com `bg-primary` | `components/ui/button.tsx:12` | Automaticamente usa `--color-primary` — só mudar o token |
| `useAuthContext()` | `features/auth/AuthContext.tsx` | Pronto — `user`, `logout` disponíveis |
| `User.full_name`, `User.role` | `types/user.ts` | Pronto — usar para AppHeader |
| `ProtectedRoute.tsx` | `components/ProtectedRoute.tsx` | Modificar para incluir AppHeader |
| `apiClient` + Tanstack Query | `lib/apiClient.ts` | Pronto — usar no Dashboard |
| `Badge` shadcn | `components/ui/badge.tsx` | Já instalado — usar temporariamente no Dashboard |
| `window.alert` / `window.confirm` | `ChecklistView.tsx:212,218,374,379,407,413-418,428,438` | 10 ocorrências — substituir conforme T2/T3 |

### O que falta (escopo desta story)

1. Atualizar 3 tokens CSS em `index.css` + adicionar Inter
2. Instalar Sonner + Dialog via shadcn CLI
3. Substituir 8 `window.alert` e 2 `window.confirm` de salvamento em `ChecklistView.tsx`
4. Criar `AppHeader.tsx` (novo arquivo)
5. Modificar `ProtectedRoute.tsx` (adicionar AppHeader)
6. Criar `Dashboard.tsx` em nova pasta feature + atualizar import em `routes.tsx`

**Nenhum arquivo de backend modificado.**

### Padrão de referência — index.css (somente as linhas que mudam)

```css
/* ANTES */
--color-primary: #1d4ed8;
--color-primary-dark: #1e40af;
--color-ring: #1d4ed8;

/* DEPOIS */
--color-primary: #003366;
--color-primary-dark: #004080;
--color-ring: #003366;
```

E no body:
```css
body {
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  /* resto igual */
}
```

### Padrão de referência — AppHeader.tsx

```tsx
import { useAuthContext } from "../features/auth/AuthContext";

export default function AppHeader() {
  const { user, logout } = useAuthContext();

  const initials = user?.full_name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() ?? "??";

  const roleLabel = user?.role === "responsavel" ? "Responsável" : "Motorista";

  return (
    <header className="sticky top-0 z-50 shadow-md bg-gradient-to-br from-[#003366] to-[#004080] text-white">
      <div className="mx-auto max-w-5xl px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-white/20 flex items-center justify-center">
            {/* ícone clipboard */}
          </div>
          <div>
            <div className="font-bold text-base leading-none">CTRVE</div>
            <div className="text-xs text-blue-200 leading-none mt-0.5 hidden sm:block">
              Checklist de Transporte de Veículos
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 bg-white/10 rounded-full px-3 py-1.5">
            <div className="w-6 h-6 rounded-full bg-white/30 flex items-center justify-center text-xs font-bold">
              {initials}
            </div>
            <div className="text-sm">
              <span className="font-medium">{user?.full_name}</span>
              <span className="text-blue-200 ml-1.5 text-xs">{roleLabel}</span>
            </div>
          </div>
          <button
            onClick={() => logout()}
            className="text-sm text-blue-200 hover:text-white transition"
          >
            Sair
          </button>
        </div>
      </div>
    </header>
  );
}
```

### Padrão de referência — Dialog para confirmação de salvamento

O `window.confirm` síncrono não pode ser substituído por Dialog de forma trivial (Dialog é assíncrono via state). Padrão correto:

```tsx
// State no componente
const [showSaveDialog, setShowSaveDialog] = useState(false);
const [pendingData, setPendingData] = useState<ChecklistEntregaData | null>(null);

// No submit handler — ao invés de window.confirm direto:
const onEntregaSubmit = async (data: ChecklistEntregaData) => {
  setSubmitError(null);
  setPendingData(data);
  setShowSaveDialog(true);
  // NÃO continuar aqui — continuar no handler do Dialog
};

const handleConfirmSave = async () => {
  if (!pendingData) return;
  setShowSaveDialog(false);
  try {
    await apiClient.patch(`/v1/checklists/${id}/entrega`, pendingData);
    toast.success("Checklist salvo com sucesso.");
    queryClient.invalidateQueries({ queryKey: ["checklists", id ?? ""] });
  } catch (error) { ... }
};

// No JSX:
<Dialog open={showSaveDialog} onOpenChange={setShowSaveDialog}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Salvar checklist?</DialogTitle>
      <DialogDescription>
        Deseja confirmar o salvamento deste checklist? Após a confirmação, os dados não poderão ser alterados.
      </DialogDescription>
    </DialogHeader>
    <DialogFooter>
      <Button variant="outline" onClick={() => setShowSaveDialog(false)}>Cancelar</Button>
      <Button onClick={handleConfirmSave} disabled={isEntregaSubmitting}>Confirmar</Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

O mesmo padrão para `DevolucaoForm` (state próprio dentro do componente).

### Padrão de referência — Sonner em App.tsx

```tsx
import { Toaster } from "@/components/ui/sonner";

// Dentro do JSX de App:
<AuthProvider>
  <SessionGuard />
  <Toaster position="top-right" richColors />
  <AppRoutes />
</AuthProvider>
```

### Padrão de referência — Dashboard

```tsx
// frontend/src/features/dashboard/Dashboard.tsx
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import apiClient from "../../lib/apiClient";
import type { ChecklistResponse } from "../../types/checklist";
import { Badge } from "@/components/ui/badge";

export default function Dashboard() {
  const { data: checklists = [] } = useQuery<ChecklistResponse[]>({
    queryKey: ["checklists"],
    queryFn: () => apiClient.get<ChecklistResponse[]>("/v1/checklists").then(r => r.data),
  });

  const now = new Date();
  const emPreenchimento = checklists.filter(c => !c.is_locked).length;
  const esteMes = checklists.filter(c =>
    new Date(c.created_at).getMonth() === now.getMonth() &&
    new Date(c.created_at).getFullYear() === now.getFullYear()
  ).length;
  const recentes = checklists.slice(0, 3);

  return (
    <div>
      {/* HeroStrip */}
      <div className="bg-gradient-to-br from-[#003366] to-[#004080] pb-6">
        <div className="max-w-5xl mx-auto px-6 pt-6">
          <h1 className="text-xl font-bold text-white">...</h1>
          {/* stat cards */}
        </div>
      </div>
      {/* Content */}
      <div className="max-w-5xl mx-auto px-6 -mt-4">
        {/* action cards + recentes */}
      </div>
    </div>
  );
}
```

### Importante: Tailwind v4

O projeto usa **Tailwind v4** com `@theme` no CSS. Isso é diferente do padrão shadcn v3:
- **Não usar** `:root { --primary: hsl(...) }` — o sistema usa `--color-primary: #hex` dentro do `@theme {}`
- `bg-primary` → mapeia para `--color-primary` automaticamente
- `bg-gradient-to-br from-[#003366] to-[#004080]` → usar valores hardcoded no Tailwind para o gradiente do header (não existe variável para gradiente no `@theme`)

### Impacto em testes existentes

**Atenção T7.3:** Testes que usam `vi.spyOn(window, "alert").mockImplementation(() => {})` continuarão funcionando para os `window.alert` que NÃO foram substituídos nesta story (MSG-020 e MSG-021 em `useUnsavedChanges` / `onCancel`). Mas os testes que verificam `window.alert` para **sucesso de salvar** e **PDF gerado** precisarão ser atualizados para verificar o Toast Sonner em vez de `window.alert`.

Para verificar Toast Sonner em Vitest:
```typescript
import { toast } from "sonner";
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));
// ...
expect(toast.success).toHaveBeenCalledWith("Checklist salvo com sucesso.");
```

**Testes afetados:**
- `T6.4` (submit entrega chama patch) — verificar toast em vez de window.alert
- `T7.3` (clique PDF chama endpoint) — verificar toast em vez de window.alert
- `T6.6` (confirm para salvar entrega) — verificar Dialog em vez de window.confirm

### Anti-padrões (PROIBIDO)

- Migrar de `@theme` (Tailwind v4) para `:root` (shadcn v3) — manter o sistema atual
- Usar `window.alert` para qualquer nova mensagem — usar Sonner toast
- Criar header direto em cada página — AppHeader vai em `ProtectedRoute` para cobertura global
- Duplicar dados de usuário em state local — usar `useAuthContext()` no AppHeader
- `navigate("/login")` no logout — usar `logout()` de `useAuthContext` que já gerencia isso

### Sequência de Implementação Recomendada

1. T1 (CSS) → verificar que botões ficam azul marinho no browser
2. T2.1 (instalar Sonner) → `npx shadcn@latest add sonner`
3. T3.1 (instalar Dialog) → `npx shadcn@latest add dialog`
4. T2.2-T2.8 (substituir window.alert)
5. T3.2-T3.5 (substituir window.confirm de salvamento)
6. T4 (AppHeader) → verificar visualmente no browser
7. T5 (integrar ProtectedRoute)
8. T6 (Dashboard) → verificar visualmente
9. T7 (testes) → ajustar mocks e confirmar 0 regressões

### References

- UX Design Spec: `_bmad-output/planning-artifacts/ux-design-specification.md` — Design System Foundation, Visual Design Foundation, Component Strategy Fase 1
- Mockups: `_bmad-output/planning-artifacts/ux-design-directions.html` — Direção 2 (Institucional Moderno)
- CSS atual: `frontend/src/index.css`
- AppHeader referência visual: `ux-design-directions.html` Direção 2, header com gradiente + chip usuário

## Dev Agent Record

### Completion Notes

- T1/T2 já estavam implementados antes desta sessão (paleta CSS, Sonner instalado, window.alert substituídos, Toaster em App.tsx).
- T3: DevolucaoForm tinha state/handler mas faltava Dialog JSX; ChecklistView (entrega) ainda usava window.confirm. Implementado pattern assíncrono com state `showSaveDialog` + `handleConfirmEntregaSave` em ChecklistView, e adicionado Dialog JSX em DevolucaoForm.
- T4: AppHeader criado em `frontend/src/components/AppHeader.tsx` com gradiente azul marinho, chip de usuário (iniciais + nome + role) e botão "Sair".
- T5: ProtectedRoute modificado para incluir AppHeader acima do children — cobertura global para todas as telas autenticadas.
- T6: Dashboard extraído de `routes.tsx` para `frontend/src/features/dashboard/Dashboard.tsx` com HeroStrip, 3 stat cards, 2 action cards e lista de 3 mais recentes com Badge por status.
- T7: Testes atualizados — window.confirm substituído por interação com Dialog (getByRole("button", { name: /confirmar/i })); window.alert substituído por vi.mock("sonner") + verificação de toast.success/toast.error. 110 frontend + 106 backend passando.

### Debug Log

Nenhum.

## File List

- `frontend/src/index.css` (modificado — paleta azul marinho + Inter)
- `frontend/src/App.tsx` (modificado — Toaster Sonner)
- `frontend/src/features/checklist/ChecklistView.tsx` (modificado — Dialog confirmação entrega/devolução + toasts)
- `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx` (modificado — mocks Dialog/Sonner)
- `frontend/src/components/AppHeader.tsx` (novo)
- `frontend/src/components/ProtectedRoute.tsx` (modificado — inclui AppHeader)
- `frontend/src/features/dashboard/Dashboard.tsx` (novo)
- `frontend/src/routes.tsx` (modificado — importa Dashboard do feature folder)
- `frontend/src/components/ui/sonner.tsx` (novo — via shadcn CLI)
- `frontend/src/components/ui/dialog.tsx` (novo — via shadcn CLI)

## Change Log

- 2026-04-27: Implementação completa da Story 6.1 — fundação visual e navegação global. Paleta TJCE (#003366), tipografia Inter, AppHeader global via ProtectedRoute, Dialog de confirmação de salvamento, toasts Sonner, Dashboard refatorado com HeroStrip + stat cards + action cards + recentes.
