---
name: tjce-ship
description: Orquestrador da fase SHIP para projetos TJCE. Use when the user asks to 'preparar release', 'gerar PML', 'executar ship', or 'fechar demanda' in TJCE projects.
---

# TJCE Ship — Orquestrador de Entrega

## Overview

Orquestrador da fase SHIP da Esteira de Desenvolvimento do TJCE. Substitui as fases "Preparando Versao", "Validando PML", "Aguardando Implantacao", "Implantado" e "Fechado" com um processo estruturado de release, validacao humana e fechamento.

Este workflow **orquestra** tres agentes TJCE existentes e scripts deterministicos:
- `tjce-agent-release` — changelog, deploy checklist, rollback plan, PML
- `tjce-agent-apf` — contagem de Pontos de Funcao
- `tjce-agent-docs` — manual do usuario

**Pre-requisito:** `/tjce-verify` concluido com status APROVADO.

**Args:** `--headless` / `-H` para execucao sem interacao. Aceita `--task-type` (nova_funcionalidade | mudanca | correcao_garantia) e `--manual` flag.

**Modo interativo:** Executa todos os steps, para nos 2 gates humanos (PML + Implantacao), fecha a demanda.

**Modo headless:** Executa ate o primeiro gate humano pendente e para com exit 2.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` if present. Resolve and apply (defaults in parens):

- `{communication_language}` (Portuguese)
- `{document_output_language}` (Portuguese Brasil)
- `{output_folder}` (`{project-root}/_bmad-output`)

In interactive mode, confirm scope before starting: identify the feature being shipped and confirm task type with the user before running the pipeline.

Detect existing `{output_folder}/release/ship-state.json` — if present, offer to resume from last checkpoint.

## Execution Flow

All steps are **sequential**. Steps 5 and 6 are **conditional and independent** — execute in parallel when both apply.

| Steps | Descricao | Route | Bloqueio |
| ----- | --------- | ----- | -------- |
| 1-3 | Pre-check + Preparar Versao + PML | Load `references/pre-check-and-release.md` | Verify nao aprovado |
| 4-7 | Gate PML + APF + Manual + Checklist | Load `references/validation-and-artifacts.md` | PML rejeitado OU artefatos faltando |
| 8-9 | Gate Implantacao + Fechamento | Load `references/deployment-and-closure.md` | Implantacao nao confirmada |

**State checkpoint:** After each step completes, update `{output_folder}/release/ship-state.json` with current step, timestamp, task type, and flags. On re-invocation, detect existing state and offer to resume.

## Error Recovery

Distinguish between "agent produced bad output" and "agent crashed":
- **Script failure:** If a script produces no valid JSON to stdout, treat as infrastructure error — report and halt (exit 1).
- **Agent unavailability:** If an agent cannot be invoked, report with instructions to verify it is installed. Do not proceed with missing artifacts.
- **PML with empty sections:** If `tjce-agent-release` produces a PML with placeholder or empty sections, treat as agent failure — do not present to the gate.

## Inegociaveis

- **PML nunca com secoes vazias ou placeholder**
- **Rollback plan sempre obrigatorio**
- **APF = 0 automatico para Correcao em Garantia** — nunca invocar tjce-agent-apf
- **Manual so quando flagged como necessario**
- **2 gates humanos obrigatorios** (PML + Implantacao) — nunca automatizados
- **Checklist final verifica 100% dos artefatos esperados**

## Headless Contract

When running with `--headless` / `-H`:

- **Exit codes:** 0 = FECHADO (all steps complete), 1 = BLOQUEADO (pre-check failed or infrastructure error), 2 = AGUARDANDO GATE HUMANO (waiting for PML validation or deployment confirmation)
- **Output:** All artifacts written to `{output_folder}/release/`. Structured verdict written to `{output_folder}/release/ship-verdict.json`.
- **Missing config:** Use defaults. Do not prompt.
- **Resume:** Use `--continue` with existing `ship-state.json` to re-enter after a human gate.

## Output Artifacts

All written to `{output_folder}/release/`:

| Artifact | Produced By | Step | Condicao |
| -------- | ----------- | ---- | -------- |
| `CHANGELOG.md` | tjce-agent-release | 2 | Sempre |
| `deploy-checklist.md` | tjce-agent-release | 2 | Sempre |
| `rollback-plan.md` | tjce-agent-release | 2 | Sempre |
| `PML.md` | tjce-agent-release (PML) | 3 | Sempre |
| `apf/contagem-detalhada.md` | tjce-agent-apf | 5 | tipo != correcao_garantia |
| `apf/resumo-apf.md` | tjce-agent-apf | 5 | tipo != correcao_garantia |
| `manual/manual-usuario.md` | tjce-agent-docs | 6 | manual_necessario |
| `ship-checklist.md` | check-deliverables.py | 7 | Sempre |
| `ship-summary.md` | generate-ship-summary.py --format markdown | 9 | Sempre |
| `ship-verdict.json` | generate-ship-summary.py | 9 | Sempre |
| `ship-state.json` | Checkpoint de estado | 1-9 | Sempre |
