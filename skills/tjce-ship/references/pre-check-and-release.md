---
name: pre-check-and-release
description: Steps 1-3 — Verify APROVADO status, detect task type, prepare version, and generate PML.
---

# Steps 1-3 — Pre-Check, Preparar Versao e Gerar PML

## Step 1 — Pre-Check

### Verify APROVADO Status

```bash
python3 scripts/check-verify-status.py {output_folder}
```

If the script returns status "fail", the verify phase has not been approved. BLOCK and exit 1. Inform the user to run `/tjce-verify` first.

### Detect Task Type and Flags

```bash
python3 scripts/detect-task-type.py {output_folder} [--type nova_funcionalidade|mudanca|correcao_garantia] [--manual]
```

If `--task-type` was passed to the workflow, forward it. Otherwise the script infers from config or requirements. In interactive mode, confirm the detected type with the user before proceeding.

The script returns `task_type` and `manual_necessario` — store these for conditional logic in later steps.

### Pre-flight: Agent Availability

Verify that the required agents are accessible:
- `tjce-agent-release` (always needed)
- `tjce-agent-apf` (needed unless correcao_garantia)
- `tjce-agent-docs` (needed only if manual_necessario)

If any required agent is unavailable, report with instructions to verify it is installed. Do not proceed with missing artifacts — halt and exit 1 in headless mode.

## Step 2 — Preparar Versao

**Delegation to tjce-agent-release:** Invoke in headless mode to produce release artifacts. The agent handles changelog generation from git history, deploy checklist creation, and rollback plan. Do not replicate this logic.

**Orchestration:**

1. Invoke `tjce-agent-release --headless` with the project context
2. Validate that the agent produced all three required artifacts:
   - `{output_folder}/release/CHANGELOG.md`
   - `{output_folder}/release/deploy-checklist.md`
   - `{output_folder}/release/rollback-plan.md`
3. If any artifact is missing, treat as agent failure — do not proceed

**Rollback plan is non-negotiable** — if the agent skips it, BLOCK.

## Step 3 — Gerar PML

**Delegation to tjce-agent-release** (capability PML): Invoke to produce the PML (Plano de Mudanca e Liberacao). The agent reads requirements, changelog, Alembic migrations, and changed configs to populate all PML sections.

**Orchestration:**

1. Invoke `tjce-agent-release --headless pml`
2. Validate PML structural integrity:
   ```bash
   python3 scripts/validate-pml.py {output_folder}/release/PML.md
   ```
3. If validation fails: BLOCK — treat as agent failure per the Inegociaveis

Validate JSON output from scripts before proceeding. If a script produces no JSON, treat as infrastructure error — report and halt (exit 1 in headless).

**Progression:** Load `references/validation-and-artifacts.md`.
