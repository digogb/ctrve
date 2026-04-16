---
name: tjce-gate-check
description: Validacao de gate entre SPEC e BUILD para projetos TJCE. Use when the user asks to 'validar gate', 'gate check', 'verificar requisitos', or 'liberar para build' in TJCE projects.
---

# TJCE Gate Check — Validacao Pre-BUILD

## Overview

Validador de gate entre Phase 2 (SPEC) e Phase 4 (BUILD) da Esteira de Desenvolvimento do TJCE. Substitui "Requisitos em Revisao" e "Pronto para Desenvolvimento" com um processo estruturado de validacao em 3 camadas: completude de artefatos, consistencia cruzada de IDs, e qualidade assistida por IA.

Executa 4 scripts deterministicos para validacao mecanica e usa o LLM apenas para avaliar qualidade de casos de teste e gerar o relatorio narrativo.

**Pre-requisito:** Artefatos de SPEC gerados (user stories, business rules, messages, test cases, architecture).

**Args:** `--headless` / `-H` para execucao sem interacao. Aceita `--task-type` (nova_funcionalidade | mudanca | correcao_garantia), `--manual`, `--data-model`, `--apf-estimate <valor>`.

**Modo interativo:** Executa todas as camadas, apresenta resultado, coleta decisoes complementares, e para no gate humano.

**Modo headless:** Executa validacao, gera relatorio + verdict.json, e exit 0 (pass) ou 1 (fail). Sem gate humano.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` if present. Resolve and apply (defaults in parens):

- `{communication_language}` (Portuguese)
- `{document_output_language}` (Portuguese Brasil)
- `{output_folder}` (`{project-root}/_bmad-output`)

In interactive mode, confirm scope before starting: identify the feature being validated and confirm the expected artifacts exist.

## Execution Flow

All steps are **sequential** except Steps 2-3 which are **independent and parallel**.

### Step 1 — Completude de Artefatos (fail-fast)

```bash
python3 scripts/check-artifacts-exist.py {output_folder} [--data-model] [--ux]
```

If any required artifact is missing: **BLOCK immediately**. Do not proceed to further validation — report what is missing and which agent can produce it.

### Steps 2-3 — Consistencia + Placeholders (parallel)

Run in parallel:

```bash
python3 scripts/validate-cross-references.py {output_folder}
python3 scripts/check-placeholders.py {output_folder}
```

### Step 4 — Qualidade Assistida por IA

Read the test cases file (`{output_folder}/tests/test-cases.md`). Assess whether each test case has a clear, verifiable expected result. Produce a `quality-findings.json` in the reports directory with findings in the standard format (severity, category, location, issue, fix).

### Step 5 — Calcular Score

```bash
python3 scripts/calculate-gate-score.py {output_folder}
```

The script reads all findings from Steps 1-4 and produces `gate-check-verdict.json` with the weighted score.

### Step 6 — Gerar Relatorio

Generate `{output_folder}/reports/gate-check-report.md` from the verdict data. Include per-layer breakdown, all findings, and remediation guidance. For items below threshold, suggest which TJCE agent to invoke (e.g., "RN-003 sem caso de teste — invocar tjce-agent-qa capability BUILD").

### Step 7 — Decisoes Complementares

**Interactive mode:** Confirm with the user:
- Tipo de tarefa: nova_funcionalidade | mudanca | correcao_garantia
- Manual necessario? Sim / Nao
- Modelo de dados se aplica? Sim / Nao
- Contagem APF estimada (valor aproximado)

Record decisions in verdict.json.

**Headless mode:** Read from CLI args. Missing values use defaults (task_type inferred or required, manual=false, data_model=false, apf_estimate=null).

### Step 8 — Gate Humano (interativo apenas)

Present the gate-check-report to the PO/Tech Lead.

| Decisao | Acao |
| ------- | ---- |
| **APROVADO** | Record in verdict.json. Feature liberada para BUILD. |
| **AJUSTAR** | Capture feedback. List exactly what needs fixing and which agent to invoke. |
| **REJEITAR** | Record reason. Feature retorna para SPEC. |

**Headless mode:** Skip gate. Exit code reflects score (0 = pass, 1 = fail).

## Inegociaveis

- **Score < 90% = bloqueio automatico** — sem excecao
- **Artefato obrigatorio faltando = falha imediata** — nao espera calcular score
- **Placeholder TODO em qualquer artefato = falha**
- **IDs orfaos = warning** — reporta mas nao bloqueia
- **Gate humano nunca automatizado** (modo interativo)

## Headless Contract

When running with `--headless` / `-H`:

- **Exit codes:** 0 = PASS (score >= 90), 1 = FAIL (score < 90 or missing artifacts)
- **Output:** `{output_folder}/reports/gate-check-verdict.json` and `gate-check-report.md`
- **Missing config:** Use defaults. Do not prompt.

## Output Artifacts

All written to `{output_folder}/reports/`:

| Artifact | Produced By | Step |
| -------- | ----------- | ---- |
| `gate-check-verdict.json` | calculate-gate-score.py | 5 |
| `gate-check-report.md` | LLM | 6 |
