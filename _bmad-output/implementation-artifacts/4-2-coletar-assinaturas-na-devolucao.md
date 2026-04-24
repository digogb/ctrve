# Story 4.2: Coletar Assinaturas na Devolução

Status: review

## Story

Como Responsável,
quero coletar a assinatura digital do Responsável e do Motorista no checklist de devolução,
para que ambas as partes confirmem as condições do veículo no momento da devolução.

## Acceptance Criteria

1. Dois campos de assinatura separados no formulário de devolução: "Assinatura do Responsável" e "Assinatura do Motorista", usando o componente `SignaturePad` existente (canvas HTML5 via `react-signature-canvas`).
2. Cada campo possui botão "Limpar" que apaga a assinatura e permite refazer (funcionalidade já implementada no `SignaturePad`).
3. Ambas opcionais nesta story — obrigatoriedade será enforced na Story 5.1 quando o botão Salvar for habilitado (MSG-014).
4. Assinaturas armazenadas como `assinatura_responsavel_devolucao` e `assinatura_motorista_devolucao` no modelo (campos já existem).
5. Modo read-only (`status === "devolvido"`): exibe assinaturas de devolução como `<img>` sem interação (já implementado em `DevolucaoReadOnly`).
6. Endpoint `PATCH /api/v1/checklists/{id}/devolucao` já aceita `assinatura_responsavel` e `assinatura_motorista` — nenhuma alteração backend necessária.
7. Testes validam integração dos SignaturePad no DevolucaoForm e persistência via API.

## Tasks / Subtasks

- [x] **T1 — Integrar `SignaturePad` no `DevolucaoForm` (AC: 1, 2)**
  - [x] Em `frontend/src/features/checklist/ChecklistView.tsx`: no `DevolucaoForm`, adicionar dois `<Controller>` com `SignaturePad` — um para `assinatura_responsavel`, outro para `assinatura_motorista`
  - [x] Posicionar após `FuelLevel` e antes do botão Salvar, com heading "Assinaturas da Devolução"
  - [x] Importar `SignaturePad` de `../signature/SignaturePad` e `Controller` de `react-hook-form` (Controller já importado)

- [x] **T2 — Testes frontend: assinaturas no DevolucaoForm (AC: 1, 2, 7)**
  - [x] Em `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx`:
    - Checklist locked+entregue (modo devolução): seção "Assinaturas da Devolução" visível com dois canvas
    - Checklist locked+entregue: botões "Limpar" visíveis para ambas assinaturas

- [x] **T3 — Testes frontend: assinaturas na DevolucaoReadOnly (AC: 5, 7)**
  - [x] Em `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx`:
    - Checklist devolvido COM assinaturas de devolução: exibe imagens na seção de devolução
    - Checklist devolvido SEM assinaturas de devolução: não exibe seção de assinaturas da devolução

- [x] **T4 — Teste backend: devolução com assinaturas (AC: 6, 7)**
  - [x] Em `backend/tests/api/test_checklists.py`:
    - `test_update_devolucao_com_assinaturas`: PATCH com assinaturas válidas → 200 + campos persistidos
    - `test_update_devolucao_assinatura_formato_invalido`: assinatura sem prefixo `data:image/png;base64,` → 422
    - `test_get_checklist_retorna_assinaturas_devolucao`: GET /{id} retorna `assinatura_responsavel_devolucao` e `assinatura_motorista_devolucao`

### Review Findings

- [ ] [Review][Patch] Adicionar teste backend: PATCH devolução sem assinaturas não altera assinaturas existentes [backend/tests/api/test_checklists.py]

## Dev Notes

### O que já existe (NÃO criar de novo)

| Item | Localização | Status |
|------|-------------|--------|
| `SignaturePad` componente | `frontend/src/features/signature/SignaturePad.tsx` | Criado na Story 3.3, funcional |
| `SignaturePad` testes | `frontend/src/features/signature/__tests__/SignaturePad.test.tsx` | 7 testes passando |
| `assinatura_responsavel_devolucao` / `assinatura_motorista_devolucao` no modelo | `backend/app/models/checklist.py` | Criados na Story 4.1 |
| `assinatura_responsavel` / `assinatura_motorista` no `ChecklistDevolucaoUpdate` schema | `backend/app/schemas/checklist.py` | Criados na Story 4.1, com `validate_base64_signature` |
| `update_devolucao` persiste assinaturas | `backend/app/services/checklist_service.py:124-127` | Já implementado |
| `assinatura_*_devolucao` no `ChecklistResponse` | `backend/app/schemas/checklist.py:108-109` | Já existem |
| `assinatura_*_devolucao` no TypeScript `ChecklistResponse` | `frontend/src/types/checklist.ts` | Já existem |
| `assinatura_*` no `checklistDevolucaoSchema` Zod | `frontend/src/features/checklist/checklistSchema.ts` | `z.string().nullable().default(null)` |
| `defaultValues` e `useEffect/reset` para assinaturas | `frontend/src/features/checklist/ChecklistView.tsx:144-145,162-163` | Já mapeiam para campos devolução |
| `DevolucaoReadOnly` com assinaturas | `frontend/src/features/checklist/ChecklistView.tsx:112-129` | Já exibe com `SignaturePad readOnly` |
| Mock de `react-signature-canvas` | `frontend/src/features/checklist/__tests__/ChecklistView.test.tsx:8-23` | Já configurado |

### O que falta (escopo desta story)

1. **DevolucaoForm UI**: Adicionar 2 `<Controller>` com `SignaturePad` no componente `DevolucaoForm` (linhas ~224-236 do `ChecklistView.tsx`, entre `FuelLevel` e o botão Salvar)
2. **Testes frontend**: Verificar que as assinaturas aparecem no formulário de devolução
3. **Testes backend**: Verificar que o PATCH devolucao aceita e persiste assinaturas

### Padrão de referência — entrega (copiar para devolução)

A entrega já integra `SignaturePad` assim em `ChecklistView.tsx:372-397`:

```tsx
<div className="mt-6 space-y-4">
  <h3 className="text-lg font-semibold">Assinaturas</h3>
  <Controller
    name="assinatura_responsavel"
    control={entregaForm.control}
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
    control={entregaForm.control}
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

Para o `DevolucaoForm`, usar o mesmo padrão mas com `control` local (do `useForm` interno ao `DevolucaoForm`) e heading "Assinaturas da Devolução".

### Teste backend — assinatura válida

Reutilizar o `VALID_SIGNATURE` já definido em `test_checklists.py:515`:

```python
VALID_SIGNATURE = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
```

### Dependências e Reutilização

| Item | Localização | Uso |
|------|-------------|-----|
| `SignaturePad` | `frontend/src/features/signature/SignaturePad.tsx` | Reutilizar sem alteração |
| `Controller` | `react-hook-form` | Já importado em `ChecklistView.tsx` |
| `DevolucaoForm` | `frontend/src/features/checklist/ChecklistView.tsx:134-242` | Adicionar Controllers |
| `VALID_SIGNATURE` | `backend/tests/api/test_checklists.py:515` | Reutilizar nos testes backend |
| `locked_checklist` fixture | `backend/tests/conftest.py:113-141` | Reutilizar nos testes backend |
| `checklist_devolucao_payload` fixture | `backend/tests/conftest.py:144-161` | Estender com assinaturas |

### Anti-padrões (PROIBIDO)

- Criar novo componente de assinatura — reutilizar `SignaturePad` existente
- Alterar o `SignaturePad.tsx` — componente está completo
- Alterar o backend (modelo, schema, service, rota) — tudo já suporta assinaturas
- Tornar assinaturas obrigatórias no Zod schema (Story 5.1)
- Alterar o `DevolucaoReadOnly` — já funciona com assinaturas de devolução
- Alterar o botão Salvar (permanece disabled até Story 5.1)
- Usar `useState` para assinaturas — usar `Controller` do react-hook-form

### Aprendizados de Stories Anteriores

| Aprendizado | De onde veio | Aplicar em 4.2 |
|-------------|--------------|----------------|
| Controller com react-hook-form para SignaturePad | Story 3.3 | Mesmo padrão no DevolucaoForm |
| Mock de react-signature-canvas com forwardRef/useImperativeHandle | Story 3.3 / ChecklistView.test.tsx | Já configurado, reutilizar |
| `fromDataURL` para restaurar assinatura pré-existente | Story 3.3 code review | Já no SignaturePad, funciona automaticamente |
| `max_length=500_000` no validator base64 | Story 3.3 code review | Já no ChecklistDevolucaoUpdate |
| Assinaturas de entrega no readOnly usam heading "Assinaturas" | Story 3.3 | Usar "Assinaturas da Devolução" para distinguir |
| DevolucaoReadOnly já tem seção de assinaturas funcional | Story 4.1 | Não duplicar |

### References

- Regras de negócio: `_bmad-output/requirements/business-rules.md` — RN-015 (obrigatoriedade — Story 5.1), RN-016 (imutabilidade após salvar)
- Mensagens: `_bmad-output/requirements/messages.md` — MSG-014 (Story 5.1)
- Story 3.3: `_bmad-output/implementation-artifacts/3-3-coletar-assinaturas-na-entrega.md` — padrão de referência completo
- Story 4.1: `_bmad-output/implementation-artifacts/4-1-preencher-checklist-de-devolucao.md` — DevolucaoForm, DevolucaoReadOnly, backend

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6

### Debug Log References

Nenhum issue encontrado — implementação limpa.

### Completion Notes List

- T1: Adicionados 2 Controllers com SignaturePad no DevolucaoForm, entre FuelLevel e botão Salvar, com heading "Assinaturas da Devolução". SignaturePad já importado no arquivo.
- T2: 2 testes frontend — seção de assinaturas visível no formulário de devolução + botões Limpar presentes.
- T3: 2 testes frontend — devolvido com assinaturas exibe imagens, devolvido sem assinaturas não exibe seção.
- T4: 3 testes backend — PATCH com assinaturas válidas (200), formato inválido (422), GET retorna campos de assinatura de devolução.

### Change Log

- 2026-04-23: Story 4.2 implementation — 4 tasks completed. Frontend: 2 Controllers SignaturePad no DevolucaoForm + 4 testes. Backend: 3 testes de assinatura de devolução.

### File List

**Modificados:**
- frontend/src/features/checklist/ChecklistView.tsx
- frontend/src/features/checklist/__tests__/ChecklistView.test.tsx
- backend/tests/api/test_checklists.py
