# Story 6.3: Formulário em Etapas e Refinamento

Status: done

## Story

Como Responsável,
quero preencher o checklist de entrega em 3 etapas guiadas (Itens → Condições → Assinaturas),
para que o processo longo seja dividido em partes gerenciáveis e eu não perca o contexto no celular.

## Acceptance Criteria

1. Formulário de entrega em `ChecklistView.tsx` dividido em 3 etapas: Etapa 1 (20 itens), Etapa 2 (combustível + data + mapa de avarias + observações), Etapa 3 (assinaturas + botão Salvar).
2. `ChecklistStepper` (criado na Story 6.2) exibido no topo do formulário com etapa atual destacada.
3. Botão "Próximo →" avança para próxima etapa e valida apenas os campos da etapa atual — não executa validação global.
4. Botão "← Voltar" entre etapas retorna à etapa anterior sem perder dados do formulário.
5. Formulário de devolução (`DevolucaoForm`) segue o mesmo padrão de 3 etapas.
6. `window.confirm` do cancel (`onCancel`) substituído por Dialog shadcn com MSG-020.
7. `useUnsavedChanges` atualizado para usar Dialog shadcn em vez de `window.confirm` para MSG-021, onde possível.
8. Layout responsivo: `grid-cols-1 sm:grid-cols-2` nos itens; formulário limitado a `max-w-2xl` no desktop.
9. Nenhuma regressão nos testes existentes — testes de navegação entre etapas adicionados.

## Tasks / Subtasks

- [x] **T1 — ChecklistView: state de etapa para entrega (AC: 1-4)**
  - [x] T1.1: Adicionar `const [entregaStep, setEntregaStep] = useState<1 | 2 | 3>(1)` no componente `ChecklistView`
  - [x] T1.2: Separar o formulário de entrega em 3 blocos condicionais por `entregaStep`
  - [x] T1.3: Etapa 1 contém: `ChecklistStepper` + `ChecklistItems` (modo edit) + contador + botão "Próximo →"
  - [x] T1.4: Validação de Etapa 1: `itens.every(i => i.status !== undefined)` — mensagem inline
  - [x] T1.5: Etapa 2 contém: `ChecklistStepper` + data/hora + `FuelLevel` + `DamageMap` + `ObservationsField` + botões "← Voltar" e "Próximo →"
  - [x] T1.6: Validação de Etapa 2: `data_entrega` e `nivel_combustivel` preenchidos
  - [x] T1.7: Etapa 3 contém: `ChecklistStepper` + 2 `SignaturePad` + botões "← Voltar" e "Salvar Checklist"
  - [x] T1.8: Botão "Salvar Checklist" na Etapa 3: abre Dialog de confirmação

- [x] **T2 — DevolucaoForm: mesma lógica de 3 etapas (AC: 5)**
  - [x] T2.1: Adicionar `const [step, setStep] = useState<1 | 2 | 3>(1)` no `DevolucaoForm`
  - [x] T2.2: Etapa 1: 20 itens de verificação
  - [x] T2.3: Etapa 2: quilometragem final + data/hora + combustível + observações; validações de KM e data inline
  - [x] T2.4: Etapa 3: 2 assinaturas + botão "Salvar Checklist"
  - [x] T2.5: `ChecklistStepper` no topo de cada etapa de `DevolucaoForm`

- [x] **T3 — Dialog para Cancel (AC: 6)**
  - [x] T3.1: `const [showCancelDialog, setShowCancelDialog] = useState(false)` adicionado
  - [x] T3.2: `onCancel` atualizado: remove `window.confirm`, seta `setShowCancelDialog(true)`
  - [x] T3.3: `handleConfirmCancel` executar DELETE + navigate
  - [x] T3.4: Dialog com título "Cancelar checklist?", descrição, botões "Descartar" e "Continuar editando"
  - [x] T3.5: Dialog renderizado fora do bloco condicional de etapas

- [x] **T4 — useUnsavedChanges: Dialog para MSG-021 (AC: 7)**
  - [x] T4.1: Avaliado — hook sem contexto JSX, Dialog requereria refatoração maior
  - [x] T4.2: Mantido `window.confirm` em `useUnsavedChanges` (over-engineering para MVP)
  - [x] T4.3: Documentado na Dev Agent Record

- [x] **T5 — Layout responsivo (AC: 8)**
  - [x] T5.1: Botões "← Voltar" e "Próximo →" em flex row com `gap-3`; Salvar com `flex-1`
  - [x] T5.2: Grid dos itens usa `grid-cols-1 sm:grid-cols-2` (herdado da Story 6.2)
  - [x] T5.3: Botões nas etapas em flex row com gap-3

- [x] **T6 — Testes (AC: 9)**
  - [x] T6.1: Testes de submit atualizados para navegar entre etapas antes de clicar "Salvar Checklist"
  - [x] T6.2: Testes de DevolucaoForm atualizados para navegar até step 3
  - [x] T6.3: Testes "Cancelar" atualizados para usar Dialog em vez de window.confirm
  - [x] T6.4: Testes "Voltar com form sujo" atualizados para usar click em botão OK em vez de campo datetime

## Dev Notes

### Dependência da Story 6.2

Esta story depende do `ChecklistStepper` criado em Story 6.2. Se 6.2 ainda não foi implementada, criar `ChecklistStepper` como stub mínimo inline e refatorar depois.

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `entregaForm` com todos os campos | `ChecklistView.tsx:337-348` | Pronto — state do form persiste entre etapas |
| `ChecklistItems`, `FuelLevel`, `DamageMap`, `SignaturePad`, `ObservationsField` | `ChecklistView.tsx` (já importados) | Pronto — apenas mover para etapas |
| `onEntregaSubmit` | `ChecklistView.tsx:370-385` | Pronto — chamar da Etapa 3 |
| Dialog shadcn | `components/ui/dialog.tsx` (instalado em Story 6.1) | Pronto |
| `showCancelDialog` pattern | Story 6.1 (Dialog para save) | Usar mesmo padrão para cancel |
| `apiClient.delete` + `navigate` no `onCancel` | `ChecklistView.tsx:428-443` | Mover para `handleConfirmCancel` |
| `ChecklistStepper` | Story 6.2 | Dependência |

### Estratégia de state entre etapas

O formulário de entrega usa `useForm` com todos os 20+ campos declarados de uma vez. As etapas são **visuais apenas** — o state do formulário persiste inteiro, não há reset entre etapas. Apenas o JSX renderizado muda via `entregaStep`.

```
entregaStep = 1 → renderiza ChecklistItems (connected to entregaForm)
entregaStep = 2 → renderiza data/hora, combustível, mapa (connected to entregaForm)
entregaStep = 3 → renderiza assinaturas (connected to entregaForm) + botão Salvar
```

`entregaForm.getValues()` sempre tem todos os dados independente da etapa. O `handleSubmit` na Etapa 3 dispara a validação Zod completa antes do PATCH.

### Validação por etapa

Não usar `trigger()` do React Hook Form para validação parcial (complexo e propenso a erros). Abordagem mais simples:

```typescript
// Avançar da Etapa 1:
const itens = entregaForm.getValues("itens");
const allMarked = itens.every(i => i.status !== undefined);
if (!allMarked) {
  setEtapa1Error("Todos os itens devem ser verificados antes de continuar.");
  return;
}
setEntregaStep(2);

// Avançar da Etapa 2:
const data_entrega = entregaForm.getValues("data_entrega");
const nivel_combustivel = entregaForm.getValues("nivel_combustivel");
if (!data_entrega || !nivel_combustivel) {
  setEtapa2Error("Preencha a data/horário e o nível de combustível.");
  return;
}
setEntregaStep(3);
```

Adicionar `const [etapa1Error, setEtapa1Error] = useState<string | null>(null)` e `etapa2Error` antes dos early returns.

### Padrão de referência — estrutura JSX das etapas

```tsx
{isFillingEntrega && (
  <Card>
    <CardContent>
      <form onSubmit={entregaForm.handleSubmit(onEntregaSubmit)}>
        {/* ChecklistStepper sempre visível */}
        <ChecklistStepper
          currentStep={entregaStep}
          steps={[
            { label: "Itens" },
            { label: "Condições" },
            { label: "Assinaturas" },
          ]}
        />

        {/* Etapa 1 */}
        {entregaStep === 1 && (
          <>
            <ChecklistItems control={entregaForm.control} errors={entregaErrors} />
            {etapa1Error && <p role="alert" className="text-sm text-danger mt-2">{etapa1Error}</p>}
            <div className="mt-6 flex gap-3">
              <Button type="button" variant="outline" onClick={onCancel}>Cancelar</Button>
              <Button type="button" className="flex-1" onClick={handleNextFromStep1}>Próximo →</Button>
            </div>
          </>
        )}

        {/* Etapa 2 */}
        {entregaStep === 2 && (
          <>
            {/* campos data, combustível, mapa, observações */}
            <div className="mt-6 flex gap-3">
              <Button type="button" variant="outline" onClick={() => setEntregaStep(1)}>← Voltar</Button>
              <Button type="button" className="flex-1" onClick={handleNextFromStep2}>Próximo →</Button>
            </div>
          </>
        )}

        {/* Etapa 3 */}
        {entregaStep === 3 && (
          <>
            {/* assinaturas */}
            {submitError && <p role="alert" className="mt-4 text-sm text-danger">{submitError}</p>}
            <div className="mt-6 flex gap-3">
              <Button type="button" variant="outline" onClick={() => setEntregaStep(2)}>← Voltar</Button>
              <Button type="submit" disabled={isEntregaSubmitting} className="flex-1">
                {isEntregaSubmitting ? "Salvando..." : "Salvar Checklist"}
              </Button>
            </div>
          </>
        )}
      </form>
    </CardContent>
  </Card>
)}
```

### Atenção: botão Cancelar nas etapas

O botão "Cancelar" (que abre o Dialog de cancel) deve aparecer apenas na Etapa 1. Na Etapa 2 e 3, o usuário usa "← Voltar" para retroceder e pode voltar à Etapa 1 para cancelar. Isso evita cancelamentos acidentais quando o usuário está quase terminando.

### Anti-padrões (PROIBIDO)

- `trigger()` do RHF para validação parcial — usar `getValues()` + validação manual por etapa
- Reset do formulário ao mudar de etapa — o state persiste; apenas o JSX muda
- Múltiplos `<form>` para as etapas — um único `<form>` wrappando todas as etapas
- Dialog para MSG-021 em `useUnsavedChanges` — manter `window.confirm` (hook não tem JSX context)
- Validação Zod por etapa — Zod valida tudo no submit final; validação manual por etapa é mais simples

### Impacto em testes existentes

Testes existentes de ChecklistView verificam submit completo do formulário (T6.4). Com a divisão em etapas, o botão "Salvar" agora está na Etapa 3. Testes precisarão:
1. Preencher todos os itens (ou simular entregaStep = 3)
2. Clicar "Próximo" até chegar na Etapa 3
3. OU: criar helper `renderAtStep3()` que pré-define `entregaStep = 3`

A abordagem mais simples: mockar o state inicial de `entregaStep` via prop ou expor a função de set. Alternativa: simular cliques de "Próximo" preenchendo os campos obrigatórios de cada etapa.

### Review Findings

- [x] [Review][Patch] `handleConfirmEntregaSave` sem guard de dupla execução — adicionado `isEntregaConfirming` state + guard + disabled [`frontend/src/features/checklist/ChecklistView.tsx:handleConfirmEntregaSave`]
- [x] [Review][Patch] Erros de etapa não limpos ao voltar — handlers "← Voltar" agora limpam `etapa1Error`/`etapa2Error`/`devStep1Error`/`devStep2Error` [`frontend/src/features/checklist/ChecklistView.tsx`]
- [x] [Review][Patch] Formulário de entrega sem `noValidate` — adicionado [`frontend/src/features/checklist/ChecklistView.tsx:688`]
- [x] [Review][Patch] Formulários limitados a `max-w-2xl` — entrega e DevolucaoForm agora envolvidos em `<div className="max-w-2xl">` [`frontend/src/features/checklist/ChecklistView.tsx`]
- [x] [Review][Patch] Testes de navegação bidirecional adicionados: "S6.3 — Próximo → sem itens exibe erro" e "S6.3 — ← Voltar retorna à etapa 1" [`frontend/src/features/checklist/__tests__/ChecklistView.test.tsx`]
- [x] [Review][Defer] Validação de data parcial em `datetime-local` — browser impede entrada parcial em uso real [`frontend/src/features/checklist/ChecklistView.tsx`] — deferred, pre-existing
- [x] [Review][Defer] `entregaForm.reset` vs `reset` desestruturado na dep array — funcionalmente idêntico com hook `useForm` [`frontend/src/features/checklist/ChecklistView.tsx:494`] — deferred, pre-existing
- [x] [Review][Defer] Etapa 3 sem pré-validação manual de assinaturas — Zod valida no submit; inconsistência UX aceitável para MVP — deferred, pre-existing
- [x] [Review][Defer] Entrega step 2 sem `setError` por campo — exibe erro genérico; DevolucaoForm mais granular; melhorar em story futura — deferred, pre-existing
- [x] [Review][Defer] `DamageMap` sem validação inline no step 2 — Zod captura no submit; fora do escopo do AC — deferred, pre-existing

## Dev Agent Record

### Completion Notes

- T1-T2: Formulário de entrega e DevolucaoForm divididos em 3 etapas visuais. State do formulário persiste completo entre etapas (apenas JSX condicional muda). Validação manual por etapa via `getValues()` — sem `trigger()` do RHF conforme anti-padrão.
- T3: `window.confirm` do Cancel substituído por Dialog shadcn com "Cancelar checklist?" / "Descartar" / "Continuar editando". `handleConfirmCancel` executa DELETE+navigate.
- T4: `window.confirm` de MSG-021 em `useUnsavedChanges` mantido — hook sem contexto JSX, refatoração seria over-engineering para MVP.
- T5: Botões de navegação em `flex gap-3`, Salvar com `flex-1`. ChecklistStepper integrado com `CHECKLIST_STEPS` constante compartilhada.
- T6: 23 testes atualizados para refletir navegação entre etapas. Adicionados helpers `navigateEntregaToStep2()` e `navigateEntregaToStep3()`. Testes de Cancel atualizados para Dialog. Testes "Voltar sujo" atualizados para click em botão OK. 113 frontend + 106 backend passando.
- Decisão arquitetural: `onEntregaSubmit` continua como `void` (sem async), simplesmente abre Dialog. A validação Zod completa ocorre via `handleSubmit` no submit do form na Etapa 3.

## File List

- `frontend/src/features/checklist/ChecklistView.tsx` (modificado — completa reescrita: etapas entrega/devolução, Cancel Dialog, ChecklistStepper integrado)
- `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx` (modificado — 23 testes atualizados + constantes FILLED_ENTREGA_CHECKLIST, COMPLETE_DEVOLUCAO_CHECKLIST, helpers de navegação)

## Change Log

- 2026-04-27: Implementação completa da Story 6.3 — formulário em 3 etapas (entrega + devolução), Dialog para cancelamento, integração do ChecklistStepper.

### References

- UX Design Spec: `_bmad-output/planning-artifacts/ux-design-specification.md` — 2.5 Experience Mechanics, Flow Optimization Principles
- ChecklistView atual: `frontend/src/features/checklist/ChecklistView.tsx`
- Story 6.1: Dialog pattern para confirmação de salvamento (mesmo padrão para cancel)
- Story 6.2: ChecklistStepper (dependência)
