---
name: tjce-verify
description: Orquestrador de verificacao em 4 camadas para projetos TJCE. Use when the user asks to 'verificar entrega', 'executar verify', or 'homologar feature' in TJCE projects.
---

# TJCE Verify — Orquestrador de Verificacao

## Overview

Orquestrador da fase VERIFY da Esteira de Desenvolvimento do TJCE. Substitui as fases "Em Teste", "Aguardando Homologacao" e "Em Homologacao" com um processo estruturado em 4 camadas: verificacao automatizada, verificacao funcional, verificacao de seguranca e homologacao humana.

Este workflow nao executa testes nem faz code review — ele **orquestra** os agentes TJCE existentes (`tjce-agent-qa`) e scripts deterministicos, consolidando resultados em um relatorio de Go/No-Go para decisao do PO.

**Args:** `--headless` / `-H` para execucao sem interacao. Para no gate humano com exit 2.

**Modo interativo:** Executa todas as camadas sequencialmente, apresenta sumario ao PO, aguarda decisao.

**Modo headless:** Executa camadas 1-3 automaticamente, gera artefato "aguardando homologacao", exit 2.

## On Activation

Load available config from `{project-root}/_bmad/config.yaml` and `{project-root}/_bmad/config.user.yaml` if present. Resolve and apply (defaults in parens):

- `{user_name}` (null)
- `{communication_language}` (Portuguese)
- `{document_output_language}` (Portuguese Brasil)
- `{output_folder}` (`{project-root}/_bmad-output`)
- `{coverage_threshold}` (80)

## Execution Flow

All stages are **sequential and mandatory** — no stage can be skipped.

| Stage | Camada | Route | Bloqueio Automatico |
| ----- | ------ | ----- | ------------------- |
| 1-2 | Pre-check + Automatizada | Load `references/pre-check-and-automated.md` | Artefatos faltando OU cobertura abaixo do threshold |
| 3-4 | Funcional + Seguranca | Load `references/functional-and-security.md` | Vulnerabilidade critica |
| 5-6 | Consolidacao + Gate | Load `references/consolidation-and-gate.md` | Decisao humana obrigatoria |

**Progression:** Each stage loads the next reference automatically upon completion. If a blocking condition is met, execution halts with diagnostic output.

## Inegociaveis

- **Nenhuma camada pode ser pulada** — todas sao obrigatorias
- **Cobertura abaixo de `{coverage_threshold}`% = bloqueio automatico**
- **Vulnerabilidade critica = bloqueio automatico**
- **Homologacao humana nunca automatizada** — em headless, gera artefato e para (exit 2)
- **Todos os relatorios versionados no Git**

## Headless Contract

When running with `--headless` / `-H`:

- **Exit codes:** 0 = APROVADO (all layers pass + PO approval in interactive), 1 = BLOQUEADO (blocking finding in any layer), 2 = AGUARDANDO HOMOLOGACAO (layers 1-3 pass, awaiting human gate)
- **Output:** All artifacts written to `{output_folder}/reports/` as in interactive mode
- **Missing config:** Use defaults. Do not prompt.
- Layers 1-3 execute fully. Layer 4 (human gate) generates `verify-summary.md` with status "AGUARDANDO HOMOLOGACAO" and exits with code 2.

## Output Artifacts

All written to `{output_folder}/reports/`:

| Artifact | Produced By |
| -------- | ----------- |
| `verify-layer1-automated.md` | Camada 1 (tjce-agent-qa VERIFY) |
| `test-cycle-N.md` | Camada 2 (tjce-agent-qa VERIFY) |
| `security-report.md` | Camada 3 (scripts deterministicos) |
| `verify-summary.md` | Consolidacao (script + workflow) |
