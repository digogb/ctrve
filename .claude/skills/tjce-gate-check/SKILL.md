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

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` if present. When neither exists, apply defaults directly:

- `{communication_language}` (Portuguese)
- `{document_output_language}` (Portuguese Brasil)
- `{output_folder}` (`{project-root}/_bmad-output`)

In interactive mode, confirm scope before starting: identify the feature being validated and confirm the expected artifacts exist.

## Execution Flow

All steps are **sequential** except Steps 2-3 which are **independent and parallel**.

### Step 1 — Completude de Artefatos (fail-fast)

```bash
python3 scripts/check-artifacts-exist.py {output_folder} -o {output_folder}/reports/artifacts-findings.json [--data-model] [--ux]
```

If any required artifact is missing: **BLOCK immediately**. Do not proceed to further validation — report what is missing and which agent can produce it.

### Steps 2-3 — Consistencia + Placeholders (parallel)

Invoke both scripts as parallel Bash tool calls in a single response:

```bash
python3 scripts/validate-cross-references.py {output_folder} -o {output_folder}/reports/crossref-findings.json
python3 scripts/check-placeholders.py {output_folder} -o {output_folder}/reports/placeholder-findings.json
```

### Step 4 — Qualidade Assistida por IA

Read the test cases file (`{output_folder}/tests/test-cases.md`). Assess whether each test case has a clear, verifiable expected result. Write `{output_folder}/reports/quality-findings.json` with findings following this schema:

```json
{"findings": [{"severity": "high", "category": "test-quality", "location": {"file": "tests/test-cases.md", "line": 42}, "issue": "CT-003 sem resultado esperado verificavel", "fix": "Adicione resultado esperado mensuravel"}]}
```

If LLM assessment is unavailable (timeout, rate limit), write `{"findings": []}` and log warning to stderr. The score calculator penalizes missing quality assessment — an empty file is better than no file.

### Step 5 — Calcular Score

```bash
python3 scripts/calculate-gate-score.py {output_folder} -o {output_folder}/reports/gate-check-verdict.json [--task-type nova_funcionalidade|mudanca|correcao_garantia] [--manual] [--data-model] [--apf-estimate <valor>]
```

The script reads all findings from Steps 1-4 and produces the weighted score. If `quality-findings.json` is absent, the quality layer scores 0/30 (not 30/30).

### Step 6 — Gerar Relatorio

Generate `{output_folder}/reports/gate-check-report.md` from the verdict data. Include per-layer breakdown, all findings, and remediation guidance. For items below threshold, suggest which TJCE agent to invoke (e.g., "RN-003 sem caso de teste — invocar tjce-agent-qa capability BUILD").

### Step 7 — Decisoes Complementares

**Interactive mode:** Confirm with the user:
- Tipo de tarefa: nova_funcionalidade | mudanca | correcao_garantia
- Manual necessario? Sim / Nao
- Modelo de dados se aplica? Sim / Nao
- Contagem APF estimada (valor aproximado)

Record decisions in gate-check-verdict.json.

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
- **Placeholder TODO em qualquer artefato = score FAIL** (via critical finding no scoring)
- **IDs orfaos = penalidade leve (low)** — reporta mas nao bloqueia
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
| `artifacts-findings.json` | check-artifacts-exist.py | 1 |
| `crossref-findings.json` | validate-cross-references.py | 2 |
| `placeholder-findings.json` | check-placeholders.py | 3 |
| `quality-findings.json` | LLM | 4 |
| `gate-check-verdict.json` | calculate-gate-score.py | 5 |
| `gate-check-report.md` | LLM | 6 |
