# Script Opportunities Analysis — tjce-agent-apf

**Scanner:** ScriptHunter (determinism audit)
**Target:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf`
**Date:** 2026-04-15

## Existing Scripts Inventory

Two Python scripts already exist under `scripts/`:

1. **`calculate-fp.py`** — Deterministic IFPUG CPM 4.3.1 complexity matrix + PF weight lookup. Accepts `--type`, `--der`, `--rlr`/`--alr`, `--json`. Handles all 5 function types (ALI/AIE/EE/SE/CE). Excellent coverage of the classification math.
2. **`validate-fp-sources.py`** — Parses `contagem-detalhada.md` tables, extracts US-NNN/RN-NNN references, cross-checks against `user-stories.md` and `business-rules.md`, reports orphan/sourceless functions with exit-code contract. Excellent coverage of source validation.

Both scripts use PEP 723 inline metadata, argparse with `--help`, `--json` output, and structured exit codes — aligned with the toolbox standard described in the scan reference.

## Assessment

The intelligence placement in this agent is **already strong**: the two most deterministic operations (IFPUG matrix classification and source cross-reference) are correctly delegated to scripts, and the prompts explicitly forbid "arbitrating" complexity. The remaining opportunities are mid-impact — chiefly a pre-pass that could inventory candidate entities/transactions from requirements before the LLM reads them, a VAF calculator that the LLM is currently doing in-prompt arithmetic for, and a post-processing validator/aggregator for the final markdown artifacts. These would trim tokens and harden determinism, but the agent is not asking the LLM to do work that is obviously script-shaped today.

## Key Findings

### Finding 1 — VAF / PF Ajustado arithmetic done in prompt (MEDIUM)

**File:** `references/count-capability.md:113-124` (Passo 6)
**What the LLM is currently doing:** Executing the formulas `VAF = (TDI * 0.01) + 0.65` and `PF Ajustado = PF Brutos * VAF`, plus the sum of PF across all functions to obtain PF Brutos, and the distribution percentages per type (Passo 7 `resumo-apf.md` table — quantity, PF, %).
**What a script would do:** A new `scripts/aggregate-fp.py` that takes the function catalogue (or the already-written `contagem-detalhada.md`) plus a `--tdi N` argument and emits PF Brutos, VAF, PF Ajustado, subtotals per type, and percentage distribution as JSON/markdown. This is pure arithmetic — 100% deterministic, trivially unit-testable, and the LLM is doing floating-point multiplication that LLMs are known to botch.
**Signal phrases matched:** "count", "total", "aggregate", "summarize statistics" (Category 4).
**Estimated token savings:** ~150–250 tokens per invocation (arithmetic reasoning + table math), plus correctness guarantee on floating-point.
**Pre-pass potential:** No — this is post-pass (after catalogue is built).
**Standalone value:** High — usable as a CI lint to recompute totals from any contagem-detalhada.md.
**Reuse across skills:** Any TJCE skill producing APF artifacts could reuse.

### Finding 2 — Requirements inventory / candidate extraction done in prompt (MEDIUM)

**File:** `references/count-capability.md:51-60` (Passo 1 — Leitura e Inventario)
**What the LLM is currently doing:** Reading the entire `user-stories.md`, `business-rules.md`, and `data-model.md` files, then producing an "inventario interno" of candidate entities (potential ALI/AIE) and candidate use cases (potential EE/SE/CE). This forces the LLM to re-read potentially large requirement artefacts end-to-end on every run.
**What a script would do:** A new `scripts/extract-fp-candidates.py` as a **pre-pass** that parses:
- `data-model.md` — extract entity names, attribute counts (DER hints), and subgroup relations (RLR hints) as JSON
- `user-stories.md` — extract US IDs, titles, acronyms like CRUD/lista/relatorio (transaction-type hints), referenced entities
- `business-rules.md` — extract RN IDs and the entities/operations they touch
Output a compact JSON inventory: `{entities: [{name, der_hint, rlr_hint, source_us}], transactions: [{us_id, verb_hint, type_hint, entities_touched}]}`.
The LLM then reads only the JSON inventory (plus targeted re-reads on ambiguity), not the raw files.
**Signal phrases matched:** "read and analyze", "scan through", "review all", "gather all" (Category 8 — Pre-Processing, "the most creative category").
**Estimated token savings:** 800–2,000+ tokens per invocation (large file ingestion replaced by compact JSON). On large TJCE projects with many US/RN this compounds.
**Pre-pass potential:** YES — this is the canonical pre-pass pattern. Feeds the LLM scanner/analyst with structured data instead of raw markdown.
**Standalone value:** Medium — useful for any requirements-reading skill.
**Reuse across skills:** High — `tjce-agent-requirements`, other APF tooling, traceability reports.

### Finding 3 — Markdown table generation boilerplate (LOW)

**File:** `references/count-capability.md:128-161` (Passo 7 — escrever artefatos)
**What the LLM is currently doing:** Formatting rows into markdown tables for `contagem-detalhada.md` (two tables) and `resumo-apf.md` (metrics + distribution table), including computing subtotals per type and the percentage distribution.
**What a script would do:** `aggregate-fp.py` (same as Finding 1) could emit the final markdown tables directly from the function list, or provide a `--markdown` mode. The LLM provides the function list + names + sources; the script lays out the tables, subtotals, and percentages.
**Signal phrases matched:** "format as", "restructure" (Category 3).
**Estimated token savings:** ~80–150 tokens per invocation (format boilerplate).
**Pre-pass potential:** No (post-pass).
**Standalone value:** Low — tightly coupled to these two artefact templates.

### Finding 4 — Structural validation of generated artefacts (LOW)

**File:** Implicit across `references/count-capability.md:14-19, 128-190`
**What the LLM is currently doing:** Nothing explicit today, but there is no post-write validation that `contagem-detalhada.md` has all required sections (Funcoes de Dados, Funcoes Transacionais, Subtotais, PF Brutos) and that `resumo-apf.md` has the metrics table + Distribution + Parecer. Structural drift can slip through.
**What a script would do:** `scripts/validate-apf-artifacts.py` — check required headers/sections, that every FD-NNN row has non-empty DER/RLR/Complexidade/PF/Fonte cells, that the sum of row PFs matches declared PF Brutos, and that VAF math matches TDI. Extends `validate-fp-sources.py`.
**Signal phrases matched:** "check structure", "required files", "verify" (Category 6 + Category 9 — post-processing).
**Estimated token savings:** Minor on direct invocation (<100 tokens), but catches silent bugs that would otherwise require LLM self-review.
**Pre-pass potential:** No (post-pass validation — Category 9).
**Standalone value:** High — usable as a CI gate.

### Finding 5 — Prerequisite file existence check (LOW)

**File:** `SKILL.md:44-56` (Prerequisite Check)
**What the LLM is currently doing:** The activation block tells the LLM to verify three file paths exist and branch messaging. This is 3 file existence checks + branching strings.
**What a script would do:** A small `scripts/check-prereqs.py` could `os.path.exists` the three paths and emit a JSON verdict `{missing: [...], can_proceed: bool, fallback: "ask-user"}`. Marginal since the LLM can easily do three exists checks via Read tool calls — but routing through a script normalizes messaging.
**Signal phrases matched:** "verify exists", "required files" (Category 6).
**Estimated token savings:** <50 tokens per invocation. Not worth building a dedicated script; the existing Read tool handles this cleanly.
**Pre-pass potential:** Marginal.
**Recommendation:** **Do not build.** Kept in the report for completeness; LLM exists-checks are fine here.

## Non-Findings (Correctly Handled)

- **IFPUG complexity matrix (ALI/AIE/EE/SE/CE)** — correctly scripted in `calculate-fp.py`. Matrices, band cutoffs, and PF weights are 100% deterministic and the prompt enforces script usage ("nunca arbitrado", `references/count-capability.md:30`).
- **Source cross-reference** — correctly scripted in `validate-fp-sources.py` with orphan/sourceless detection and exit-code contract.
- **Correcao em Garantia fast-path** — a hard-coded template write; no deterministic logic hidden behind LLM judgment. Correctly kept in-prompt since the content is trivial and the "garantia" decision is a human/user judgment call.

## Aggregate Savings

| Finding | Severity | Tokens per invocation |
|---------|----------|-----------------------|
| 1 — VAF/aggregation arithmetic | Medium | 150–250 |
| 2 — Requirements inventory pre-pass | Medium | 800–2,000+ |
| 3 — Markdown table boilerplate | Low | 80–150 |
| 4 — Artefact structural validator | Low | <100 (+ correctness gate) |
| 5 — Prereq existence check | Low | <50 (not worth building) |

**Estimated aggregate savings per run (Findings 1+2+3 implemented):** ~1,000–2,400 tokens per full contagem invocation, with the bulk coming from Finding 2's pre-pass on large requirement corpora. Findings 1 and 4 also eliminate arithmetic-error risk and structural-drift risk that the LLM currently absorbs.

**Priority recommendation:**
1. **Finding 2** (pre-pass `extract-fp-candidates.py`) — highest token savings and compounds with project size.
2. **Finding 1** (`aggregate-fp.py` with VAF/totals) — deterministic math the LLM should never be doing; can also cover Finding 3 via `--markdown`.
3. **Finding 4** (artefact validator) — low-cost hardening, pairs well with existing `validate-fp-sources.py`.
