---
name: deployment-and-closure
description: Steps 8-9 — Deployment human gate with RDM tracking and final closure with ship summary.
---

# Steps 8-9 — Implantacao e Fechamento

## Step 8 — Gate Humano: Implantacao (Parada Obrigatoria)

Human deployment authorization is **never automated**.

### Interactive Mode

Present the ship-checklist to the PO:

- All deliverables verified complete
- Deploy checklist and rollback plan ready
- PML validated by DevOps

**Await deployment confirmation:**

| Decisao | Acao |
| ------- | ---- |
| **IMPLANTADO** | Capture RDM number (Requisicao de Mudanca) and deployment date from PO. Record in ship-state.json. Proceed to Step 9. |
| **ADIADO** | Record reason and expected date in ship-state.json. Exit 2 in headless, inform in interactive. |

### Headless Mode

Write `ship-state.json` with stage=8 and status=awaiting_deployment. Exit with code 2.

## Step 9 — Fechamento

Generate the final ship summary:

```bash
python3 scripts/generate-ship-summary.py {output_folder} --task-type {task_type} [--manual-required] [--rdm {rdm_number}]
python3 scripts/generate-ship-summary.py {output_folder} --task-type {task_type} [--manual-required] [--rdm {rdm_number}] --format markdown -o {output_folder}/release/ship-summary.md
```

The script reads all release artifacts, aggregates status, and produces:
- `ship-verdict.json` — structured data for automation
- `ship-summary.md` — human-readable final report

### Interactive Mode

Present the ship-summary to the PO. Confirm closure. Update ship-state.json with stage=9, status=closed.

### Headless Mode

Write both artifacts and exit with code 0 (success).

**Pipeline complete.** Demanda fechada.
