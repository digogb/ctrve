# Story 6.2: Componentes de Domínio

Status: done

## Story

Como usuário do CTRVE,
quero componentes visuais específicos do domínio (badges de status, checklist em cards e mapa de progresso),
para que o estado de cada checklist seja imediatamente compreensível e o preenchimento seja mais fluido.

## Acceptance Criteria

1. `StatusBadge` com variantes visuais por status: "Em preenchimento" (âmbar), "Entregue" (azul), "Devolvido" (verde) — cada variante tem cor de fundo + cor de texto + label textual.
2. `ChecklistList.tsx` atualizado: substituir tabela por lista de cards estilo Direção 2 — cada card tem ícone colorido por status + placa em destaque + Nº + unidade + data + `StatusBadge`.
3. `ChecklistItems.tsx` modo editável refatorado: cada item como card com área clicável mínima de 44px; estados visuais distintos — OK (fundo verde, borda verde), Não OK (fundo vermelho, borda vermelha), Pendente (fundo branco, borda cinza).
4. Contador em tempo real "X / 20 itens verificados" visível acima dos itens no modo editável.
5. `ChecklistStepper.tsx` criado: pills numeradas horizontais (1 Itens / 2 Condições / 3 Assinaturas), barra de progresso colorida, props `currentStep` e `steps`.
6. Nenhuma regressão nos testes existentes.

## Tasks / Subtasks

- [x] **T1 — StatusBadge: criar componente (AC: 1)**
  - [x] T1.1: Criar `frontend/src/components/StatusBadge.tsx`
  - [x] T1.2: Props: `status: ChecklistResponse["status"]`, `isLocked: boolean`
  - [x] T1.3: Lógica de variante:
    - `!isLocked` → âmbar: `bg-amber-50 text-amber-700 border border-amber-200`, label "Em preenchimento"
    - `isLocked && status === "entregue"` → azul: `bg-blue-50 text-blue-700 border border-blue-200`, label "Entregue"
    - `status === "devolvido"` → verde: `bg-green-50 text-green-700 border border-green-200`, label "Devolvido"
  - [x] T1.4: Renderizar como `<span className="px-2.5 py-1 rounded-full text-xs font-semibold ...">`, não usar Badge shadcn (estilo diverge)

- [x] **T2 — ChecklistList: refatorar para cards (AC: 2)**
  - [x] T2.1: Importar `StatusBadge` de `../../components/StatusBadge`
  - [x] T2.2: Substituir `<Table>` por `<div className="space-y-2.5">` com um card por checklist
  - [x] T2.3: Cada card: `bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md cursor-pointer transition`
  - [x] T2.4: Ícone de status à esquerda em círculo colorido (âmbar/azul/verde por estado)
  - [x] T2.5: Conteúdo central: placa em bold + Nº + unidade + data formatada
  - [x] T2.6: `StatusBadge` à direita
  - [x] T2.7: Clicar no card navega para `/checklists/${c.id}` via `navigate`
  - [x] T2.8: Manter lógica de busca, loading e MSG-009 existentes — apenas substituir o JSX de renderização

- [x] **T3 — ChecklistItems: refatorar modo editável (AC: 3, 4)**
  - [x] T3.1: No modo editável de `ChecklistItems.tsx`, substituir o layout atual por grid de cards `grid-cols-1 sm:grid-cols-2 gap-2.5`
  - [x] T3.2: Cada item: `<div className="rounded-xl border px-4 py-3 flex items-center justify-between min-h-[52px] transition-colors">` com classe condicional por estado
  - [x] T3.3: Estado OK: `bg-green-50 border-green-400`; Não OK: `bg-red-50 border-red-400`; Pendente: `bg-white border-gray-200`
  - [x] T3.4: Dois botões por item: "✓ OK" e "✗ Não OK" de `px-3 py-1.5 rounded-lg text-xs font-semibold`. Botão ativo: cor sólida (verde ou vermelho). Botão inativo: branco com borda.
  - [x] T3.5: Adicionar contador acima do grid: `<div className="flex items-center justify-between mb-3"><span>Itens de Verificação</span><span>{verificados} / {total} verificados</span></div>`
  - [x] T3.6: `verificados` calculado via `useWatch` do React Hook Form

- [x] **T4 — ChecklistStepper: criar componente (AC: 5)**
  - [x] T4.1: Criar `frontend/src/features/checklist/ChecklistStepper.tsx`
  - [x] T4.2: Props: `currentStep: number`, `steps: { label: string }[]`
  - [x] T4.3: Barra de progresso: `<div style={{ width: \`${(currentStep/steps.length)*100}%\` }} className="h-1 bg-[#003366] transition-all" />`
  - [x] T4.4: Pills: flex container horizontal com scroll, cada pill `rounded-full px-3 py-1.5 text-xs`
    - Ativa: `bg-[#003366] text-white font-semibold`
    - Concluída: `bg-green-600 text-white`
    - Futura: `bg-gray-100 text-gray-400`
  - [x] T4.5: Exibir número + label em cada pill

### Review Findings

- [x] [Review][Decision] Semântica do contador "verificados" — aceito: "verificados" = itens respondidos (ok + nao_ok), conforme inspeção de veículo onde verificar ≠ aprovar [`frontend/src/features/checklist/ChecklistItems.tsx:ChecklistItemsEdit`]
- [x] [Review][Patch] `CHECKLIST_ITEMS.indexOf(item)` dentro de `.map()` — corrigido para `.map((item, index) =>)` [`frontend/src/features/checklist/ChecklistItems.tsx`]
- [x] [Review][Patch] Barra de progresso em 100% quando `currentStep === steps.length` — corrigido para `Math.max(0, Math.min(((currentStep - 1) / steps.length) * 100, 100))` [`frontend/src/features/checklist/ChecklistStepper.tsx`]
- [x] [Review][Patch] `key={i}` nas pills do Stepper — corrigido para `key={step.label}` [`frontend/src/features/checklist/ChecklistStepper.tsx`]
- [x] [Review][Patch] Botões "✓ OK" e "✗ Não OK" sem `aria-label`/`aria-pressed` — adicionados `aria-label` contextual e `aria-pressed` [`frontend/src/features/checklist/ChecklistItems.tsx`]
- [x] [Review][Patch] SVG decorativo em `StatusIcon` sem `aria-hidden` — adicionado `aria-hidden="true"` [`frontend/src/features/checklist/ChecklistList.tsx:StatusIcon`]
- [x] [Review][Patch] Cobertura de `is_locked: false` ausente nos testes — adicionado teste "exibe 'Em preenchimento' para checklist não bloqueado" [`frontend/src/features/checklist/__tests__/ChecklistList.test.tsx`]
- [x] [Review][Defer] Lógica duplicada entre `StatusBadge` e `StatusIcon` (mesma condição `!isLocked/devolvido/default`) — divergência futura em manutenção; extrair helper quando necessário — deferred, pre-existing
- [x] [Review][Defer] Botões OK/Não OK não permitem desmarcar (voltar para `undefined`) — spec não exige esta funcionalidade — deferred, pre-existing
- [x] [Review][Defer] `StatusBadge` sem guard explícita `status === "entregue"` no else — seguro com tipos TypeScript atuais — deferred, pre-existing
- [x] [Review][Defer] `border-gray-200` (Pendente) pode ter baixo contraste sobre fundo branco — melhoria visual futura — deferred, pre-existing

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `Badge` shadcn | `components/ui/badge.tsx` | Não usar para StatusBadge — estilo diverge do design |
| `ChecklistItems` edit/readonly | `features/checklist/ChecklistItems.tsx` | Modificar apenas modo edit; modo readonly NÃO mudar |
| `ChecklistList` com tabela | `features/checklist/ChecklistList.tsx` | Refatorar JSX de listagem — manter lógica de busca |
| `ChecklistResponse.status` | `types/checklist.ts` | `"entregue" \| "devolvido"` |
| `ChecklistResponse.is_locked` | `types/checklist.ts` | Necessário para distinguir "Em preenchimento" de "Entregue" |
| `useNavigate` em ChecklistList | `ChecklistList.tsx:3` | Já importado |

### O que falta (escopo desta story)

1. `StatusBadge.tsx` — novo componente em `components/`
2. `ChecklistStepper.tsx` — novo componente em `features/checklist/`
3. Refatorar JSX de listagem em `ChecklistList.tsx` (lógica intacta)
4. Refatorar JSX de modo editável em `ChecklistItems.tsx` (modo readonly intacto)

**ChecklistStepper não é conectado ao ChecklistView nesta story** — Story 6.3 faz a integração com o fluxo de 3 etapas.

### Padrão de referência — StatusBadge.tsx

```tsx
import type { ChecklistResponse } from "../types/checklist";

interface StatusBadgeProps {
  status: ChecklistResponse["status"];
  isLocked: boolean;
}

export default function StatusBadge({ status, isLocked }: StatusBadgeProps) {
  if (!isLocked) {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
        Em preenchimento
      </span>
    );
  }
  if (status === "devolvido") {
    return (
      <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700 border border-green-200">
        Devolvido
      </span>
    );
  }
  return (
    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
      Entregue
    </span>
  );
}
```

### Padrão de referência — ChecklistList (card por item)

```tsx
// Substituir o bloco de renderização da tabela por:
<div className="space-y-2.5">
  {data.map((c) => (
    <div
      key={c.id}
      onClick={() => navigate(`/checklists/${c.id}`)}
      className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 flex items-center justify-between hover:shadow-md cursor-pointer transition"
    >
      <div className="flex items-center gap-4">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
          !c.is_locked ? "bg-amber-50" : c.status === "devolvido" ? "bg-green-50" : "bg-blue-50"
        }`}>
          {/* ícone SVG por estado */}
        </div>
        <div>
          <div className="font-semibold text-gray-800">
            {c.placa}
            <span className="font-normal text-gray-400 text-sm ml-2">• Nº {c.id}</span>
          </div>
          <div className="text-xs text-gray-400">
            {c.unidade} • {c.motorista} • {formatDate(c.created_at)}
          </div>
        </div>
      </div>
      <StatusBadge status={c.status} isLocked={c.is_locked} />
    </div>
  ))}
</div>
```

### Padrão de referência — ChecklistItems contador

Para calcular `verificados` dentro do Controller, usar `useWatch`:
```tsx
import { useWatch } from "react-hook-form";

// dentro do componente ChecklistItems (modo edit):
const watchedItems = useWatch({ control: props.control, name: "itens" });
const verificados = watchedItems?.filter(i => i.status !== undefined).length ?? 0;
```

### Anti-padrões (PROIBIDO)

- Modificar o modo `readOnly` de `ChecklistItems` — apenas o modo edit muda
- Usar `<Table>` no novo ChecklistList — usar `<div>` cards
- Usar Badge shadcn como base para StatusBadge — estilo próprio (rounded-full, border)
- Conectar ChecklistStepper ao ChecklistView nesta story — isso é escopo de Story 6.3

### Impacto em testes existentes

Os testes de `ChecklistView.test.tsx` verificam elementos da UI por role/text. As mudanças visuais nos cards dos itens (novas classes) não devem quebrar testes que verificam comportamento (submit, errors, etc.). Verificar se algum teste verifica classes CSS específicas ou estrutura HTML — ajustar se necessário.

Os testes de `ChecklistList.test.tsx` verificam texto e tabela — precisarão ser atualizados para usar os novos seletores de card.

## Dev Agent Record

### Completion Notes

- T1: `StatusBadge.tsx` criado em `components/` com lógica de variante exata do spec (âmbar/azul/verde).
- T2: `ChecklistList.tsx` refatorado — Table removida, substituída por cards com `StatusIcon` + `StatusBadge`. Lógica de busca/loading/MSG-009 intacta. Mock de teste atualizado para `is_locked: true` para refletir semântica correta do StatusBadge.
- T3: `ChecklistItems.tsx` edit mode extraído para `ChecklistItemsEdit` (necessário para usar `useWatch` sem violar hooks rules). Modo readonly inalterado. Contador via `useWatch`. Testes atualizados: radio → button assertions, 2 novos testes de contador.
- T4: `ChecklistStepper.tsx` criado com barra de progresso e pills numeradas. Não conectado ao ChecklistView (escopo de Story 6.3).
- Testes: 112 frontend + 106 backend passando, zero regressões.

## File List

- `frontend/src/components/StatusBadge.tsx` (novo)
- `frontend/src/features/checklist/ChecklistStepper.tsx` (novo)
- `frontend/src/features/checklist/ChecklistList.tsx` (modificado)
- `frontend/src/features/checklist/ChecklistItems.tsx` (modificado)
- `frontend/src/features/checklist/__tests__/ChecklistItems.test.tsx` (modificado)
- `frontend/src/features/checklist/__tests__/ChecklistList.test.tsx` (modificado)

## Change Log

- 2026-04-27: Implementação completa da Story 6.2 — componentes de domínio. StatusBadge, cards em ChecklistList, grid de cards em ChecklistItems com contador, ChecklistStepper.

### References

- UX Design Spec: `_bmad-output/planning-artifacts/ux-design-specification.md` — 2.5 Experience Mechanics (Etapa 1), Component Strategy Fase 2
- Mockups: `_bmad-output/planning-artifacts/ux-design-directions.html` — Direção 2, tela de checklist
- ChecklistItems atual: `frontend/src/features/checklist/ChecklistItems.tsx`
- ChecklistList atual: `frontend/src/features/checklist/ChecklistList.tsx`
