# Workflow Integrity Analysis — tjce-ship

**Scanner:** WorkflowIntegrityBot  
**Skill:** `skills/tjce-ship`  
**Date:** 2026-04-16  
**Pre-pass override:** `workflow_type: "simple-utility"` from pre-pass is INCORRECT. This skill uses `references/` for progressive disclosure, which is a valid complex-workflow pattern. Analysis proceeds accordingly.

---

## 1. Frontmatter

| Check | Status | Notes |
| ----- | ------ | ----- |
| `name` present | PASS | `tjce-ship` |
| `description` present | PASS | Starts with role summary, includes trigger phrases |
| Description format | PASS | "Use when the user asks to..." pattern with 4 concrete trigger phrases |

**Verdict:** PASS — no issues.

---

## 2. Required Sections

| Section | Present | Line | Notes |
| ------- | ------- | ---- | ----- |
| Overview | Yes | 8 | Clear scope statement, lists orchestrated agents, pre-requisite, args |
| On Activation | Yes | 25 | Config loading, resume detection, interactive confirmation |
| Execution Flow | Yes | 37 | Routing table with 3 reference files |
| Error Recovery | Yes | 49 | Distinguishes agent failure vs. infrastructure error |
| Inegociaveis | Yes | 56 | 6 non-negotiable rules |
| Headless Contract | Yes | 65 | Exit codes, output paths, resume flag |
| Output Artifacts | Yes | 74 | Full artifact inventory with conditions |

**Verdict:** PASS — all required sections present. Additional domain sections (Error Recovery, Inegociaveis, Output Artifacts) add value without over-specifying.

---

## 3. Reference File Integrity

### 3a. Routing Table Completeness

The Execution Flow table references 3 files:

| Route in SKILL.md | File Exists | Frontmatter Valid |
| ------------------ | ----------- | ----------------- |
| `references/pre-check-and-release.md` | Yes | name: `pre-check-and-release`, description present |
| `references/validation-and-artifacts.md` | Yes | name: `validation-and-artifacts`, description present |
| `references/deployment-and-closure.md` | Yes | name: `deployment-and-closure`, description present |

### 3b. Step Coverage

SKILL.md declares steps 1-9. Reference files cover:

| Reference File | Declared Steps | Actual Steps Found |
| -------------- | -------------- | ------------------ |
| `pre-check-and-release.md` | 1-3 | Step 1 (Pre-Check), Step 2 (Preparar Versao), Step 3 (Gerar PML) |
| `validation-and-artifacts.md` | 4-7 | Step 4 (Gate PML), Step 5 (APF), Step 6 (Manual), Step 7 (Checklist) |
| `deployment-and-closure.md` | 8-9 | Step 8 (Gate Implantacao), Step 9 (Fechamento) |

Full coverage: steps 1-9 accounted for. No gaps, no overlaps.

### 3c. Progression Directives

| From File | Progression Statement | Target |
| --------- | -------------------- | ------ |
| `pre-check-and-release.md` | "Load `references/validation-and-artifacts.md`" (line 67) | Correct |
| `validation-and-artifacts.md` | "Load `references/deployment-and-closure.md`" (line 74) | Correct |
| `deployment-and-closure.md` | "Pipeline complete. Demanda fechada." (line 52) | Terminal — correct |

**Verdict:** PASS — all references resolve, steps fully covered, progression chain is complete and linear.

---

## 4. Script References

### 4a. Scripts Referenced in Reference Files

| Script Reference | File | Actual Script Exists |
| ---------------- | ---- | -------------------- |
| `scripts/check-verify-status.py {output_folder}` | pre-check-and-release.md:13 | Yes |
| `scripts/detect-task-type.py {output_folder} [--type ...] [--manual]` | pre-check-and-release.md:20 | Yes |
| `scripts/check-deliverables.py {output_folder} --task-type {task_type} [--manual-required]` | validation-and-artifacts.md:64 | Yes |
| `scripts/generate-ship-summary.py {output_folder} ...` | deployment-and-closure.md:35-37 | Yes |

### 4b. Script CLI Consistency

| Script | Doc Invocation | Actual CLI Args | Match |
| ------ | -------------- | --------------- | ----- |
| `check-verify-status.py` | `{output_folder}` | positional `output_folder` | PASS |
| `detect-task-type.py` | `{output_folder} [--type ...] [--manual]` | positional `output_folder`, `--type`, `--manual` | PASS |
| `check-deliverables.py` | `{output_folder} --task-type {task_type} [--manual-required]` | positional `output_folder`, `--task-type` (required), `--manual-required` | PASS |
| `generate-ship-summary.py` | `{output_folder} --task-type {task_type} [--manual-required] [--rdm {rdm_number}] [--format markdown] [-o ...]` | positional `output_folder`, `--task-type` (required), `--manual-required`, `--rdm`, `--format`, `-o` | PASS |

### 4c. Script Output Artifacts vs. SKILL.md Artifact Table

| Artifact in SKILL.md | Produced By (SKILL.md) | Actual Producer |
| -------------------- | ---------------------- | --------------- |
| `ship-checklist.md` | `check-deliverables.py` | Script generates markdown via `format_markdown()` but the workflow instructions (validation-and-artifacts.md:72) say to write the checklist only when the script passes. The script itself does not auto-write `ship-checklist.md` — it outputs to stdout or `-o`. The orchestrator must capture and write it. | Consistent with orchestration pattern |
| `ship-summary.md` | `generate-ship-summary.py --format markdown` | Script supports `--format markdown` and `-o` flag | PASS |
| `ship-verdict.json` | `generate-ship-summary.py` | Script outputs JSON by default with `verdict` field | PASS |

**Verdict:** PASS — all 4 scripts exist, CLI signatures match documentation, output artifacts align.

---

## 5. Language Directness

| Check | Status | Notes |
| ----- | ------ | ----- |
| No hedging language | PASS | No "try to", "you should consider", "it might be helpful" |
| No over-specification | PASS | Agent delegations say "do not replicate this logic" — correctly avoids re-specifying agent internals |
| Imperative directives | PASS | Uses direct verbs: "BLOCK", "Invoke", "Validate", "Report and halt" |
| No redundant context | PASS | Each reference file covers only its steps without repeating SKILL.md content |

**Verdict:** PASS — language is direct and action-oriented.

---

## 6. Config Integration

### 6a. On Activation Config Loading

SKILL.md specifies loading from:
- `{project-root}/_bmad/config.yaml`
- `{project-root}/_bmad/config.user.yaml`

Config keys resolved: `{communication_language}`, `{document_output_language}`, `{output_folder}`.

### 6b. Config Usage in Scripts

`detect-task-type.py` reads config from `{output_folder}/config.json` and falls back to `{output_folder}/../_bmad/config.yaml`. The path construction (`output_folder.parent / "_bmad"`) assumes `output_folder` is a direct child of project root (e.g., `project-root/_bmad-output`). This is consistent with the default `{output_folder}` value.

### 6c. Headless Defaults

SKILL.md Headless Contract states: "Missing config: Use defaults. Do not prompt." Defaults are declared in On Activation with parens notation.

**Verdict:** PASS — config integration is consistent.

---

## 7. Headless Mode Contract

### 7a. Exit Code Mapping

| Code | SKILL.md Meaning | Enforced In Reference Files |
| ---- | ---------------- | --------------------------- |
| 0 | FECHADO | deployment-and-closure.md:50 — "exit with code 0 (success)" after Step 9 |
| 1 | BLOQUEADO | pre-check-and-release.md:16 — "BLOCK and exit 1"; validation-and-artifacts.md:70 — "Exit 1 in headless" |
| 2 | AGUARDANDO GATE HUMANO | validation-and-artifacts.md:28 — "Exit with code 2" (PML gate); deployment-and-closure.md:29 — "Exit 2 in headless" (Deployment gate) |

### 7b. Human Gate Coverage

| Gate | Step | Interactive Behavior | Headless Behavior | Consistent |
| ---- | ---- | -------------------- | ----------------- | ---------- |
| PML Validation | 4 | Present PML, await APROVADO/AJUSTAR | Write state, exit 2 | PASS |
| Deployment Confirmation | 8 | Present checklist, await IMPLANTADO/ADIADO | Write state, exit 2 | PASS |

### 7c. Resume Mechanism

SKILL.md declares `--continue` flag for re-entry after human gate. On Activation detects existing `ship-state.json` and offers resume. Reference files write stage number and status to `ship-state.json` at each gate.

**Verdict:** PASS — headless contract is fully specified and consistently enforced across all reference files.

---

## 8. Cross-File Logical Consistency

### 8a. Conditional Logic Alignment

| Condition | SKILL.md | pre-check-and-release.md | validation-and-artifacts.md |
| --------- | -------- | ------------------------ | --------------------------- |
| APF skip for correcao_garantia | Inegociaveis: "APF = 0 automatico para Correcao em Garantia" | detect-task-type.py returns `task_type` | Step 5: explicit skip + placeholder write |
| Manual conditional | Args: `--manual` flag | detect-task-type.py returns `manual_necessario` | Step 6: conditional on `manual_necessario == true` |
| PML empty sections | Inegociaveis: "PML nunca com secoes vazias" | Step 3: validates no placeholders/TODO/empty | Step 4: gate never automated |

All conditional branches are consistently defined and enforced.

### 8b. Artifact Path Consistency

All files use `{output_folder}/release/` as the base path for release artifacts. Sub-paths are consistent:
- `apf/contagem-detalhada.md` and `apf/resumo-apf.md` — same in SKILL.md table, reference files, and both scripts (`check-deliverables.py`, `generate-ship-summary.py`)
- `manual/manual-usuario.md` — same everywhere

### 8c. Agent Delegation Consistency

| Agent | SKILL.md Overview | Reference File Usage | Alignment |
| ----- | ----------------- | -------------------- | --------- |
| `tjce-agent-release` | changelog, deploy checklist, rollback plan, PML | Step 2 (3 artifacts), Step 3 (PML) | PASS |
| `tjce-agent-apf` | contagem de Pontos de Funcao | Step 5 (conditional) | PASS |
| `tjce-agent-docs` | manual do usuario | Step 6 (conditional) | PASS |

### 8d. Parallelism Declaration

SKILL.md states "Steps 5 and 6 are conditional and independent — execute in parallel when both apply." Reference file `validation-and-artifacts.md` line 32 echoes: "Steps 5 and 6 are independent — execute in parallel when both apply." Consistent.

### 8e. Minor Observation — Step 6 Placeholder for Skipped Manual

`validation-and-artifacts.md` Step 6 writes a placeholder `manual-usuario.md` even when manual is not needed. However, `check-deliverables.py` only checks for `manual/manual-usuario.md` when `manual_required=True`. This means the placeholder is written but never validated — not a bug, just a defensive pattern. The checklist in `check-deliverables.py` also only includes manual artifacts when `manual_required=True`, so the placeholder won't appear in the checklist. This is fine — the placeholder exists for documentation completeness but the script correctly does not treat its absence as failure when manual is not required.

---

## Summary

| Category | Verdict | Issues |
| -------- | ------- | ------ |
| 1. Frontmatter | PASS | 0 |
| 2. Required Sections | PASS | 0 |
| 3. Reference File Integrity | PASS | 0 |
| 4. Script References | PASS | 0 |
| 5. Language Directness | PASS | 0 |
| 6. Config Integration | PASS | 0 |
| 7. Headless Mode Contract | PASS | 0 |
| 8. Cross-File Consistency | PASS | 0 |

**Overall Verdict: PASS**

**Total issues: 0 critical, 0 high, 0 medium, 0 low**

The skill is structurally complete and internally consistent. The progressive disclosure pattern via `references/` is well-executed: SKILL.md provides the routing table and contract, each reference file covers its step range without redundancy, progression directives form a complete chain, and all script invocations match their actual CLI interfaces. The headless contract is fully honored with correct exit codes at every decision point. Conditional logic for task types and the manual flag is consistently propagated from detection through execution to validation.
