---
name: validation-and-artifacts
description: Steps 4-7 — PML human gate, conditional APF counting, conditional manual generation, and deliverables checklist.
---

# Steps 4-7 — Validacao PML, Artefatos Condicionais e Checklist

## Step 4 — Gate Humano: Validar PML (Parada Obrigatoria)

Human validation of the PML is **never automated**.

### Interactive Mode

Present the PML content to the DevOps / Gerente de Configuracao:

- Highlight key sections: migrations, config changes, dependencies, rollback procedures
- Flag any sections that appear thin or generic

**Await decision:**

| Decisao | Acao |
| ------- | ---- |
| **APROVADO** | Mark PML as validated in ship-state.json. Proceed to Step 5. |
| **AJUSTAR** | Capture specific feedback. Re-invoke `tjce-agent-release --headless pml` with the feedback context. Return to PML validation. |

### Headless Mode

Write `ship-state.json` with stage=4 and status=awaiting_pml_validation. Exit with code 2.

## Steps 5-6 — Artefatos Condicionais

**Steps 5 and 6 are independent — execute in parallel** when both apply. If only one applies, execute it alone.

### Step 5 — Contagem APF (Condicional)

**Condition:** `task_type != "correcao_garantia"`

**If correcao_garantia:** Skip APF invocation entirely. Write a minimal `{output_folder}/release/apf/resumo-apf.md` with: "Correcao em Garantia — contagem APF nao aplicavel. PF = 0." This is non-negotiable — never invoke tjce-agent-apf for warranty fixes.

**If nova_funcionalidade or mudanca:**

1. Invoke `tjce-agent-apf --headless`
2. Validate outputs exist:
   - `{output_folder}/release/apf/contagem-detalhada.md`
   - `{output_folder}/release/apf/resumo-apf.md`
3. If missing, treat as agent failure

### Step 6 — Gerar Manual (Condicional)

**Condition:** `manual_necessario == true`

**If manual not needed:** Write a minimal `{output_folder}/release/manual/manual-usuario.md` with: "Manual do usuario nao aplicavel para esta entrega." Proceed.

**If manual needed:**

1. Invoke `tjce-agent-docs --headless`
2. Validate output exists: `{output_folder}/release/manual/manual-usuario.md`
3. If missing, treat as agent failure

## Step 7 — Checklist Final de Entregaveis

Run the deliverables checker with the task context:

```bash
python3 scripts/check-deliverables.py {output_folder} --task-type {task_type} [--manual-required]
```

The script validates that every expected artifact exists based on task type and flags. It produces JSON output and optionally a markdown checklist.

**If any required artifact is missing:** BLOCK. Report exactly which artifacts are missing and which step should have produced them. Exit 1 in headless.

**If all present:** Write `{output_folder}/release/ship-checklist.md` with the complete deliverables inventory.

**Progression:** Load `references/deployment-and-closure.md`.
