# Agent Cohesion Analysis — tjce-agent-apf

**Scanner:** CohesionBot
**Date:** 2026-04-15
**Target:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf`

## Assessment

The `tjce-agent-apf` agent is a tightly cohered, single-purpose specialist. Its persona (a precise, deterministic IFPUG CPM 4.3.1 Function Point analyst), its one capability (CONTAGEM), and its supporting assets (the `calculate-fp.py` and `validate-fp-sources.py` scripts) form an unusually coherent triad — the agent does exactly what it claims, with strong anti-arbitrariness guardrails baked into both persona and tooling. The narrow scope is a strength, not a weakness, for a contractual-measurement role.

## Cohesion Dimensions

### 1. Persona-Capability Alignment — **Strong**

The persona declares "determinismo IFPUG", "rastreabilidade total", "nao contar em dobro", and "pergunte, nao assuma". Every one of these principles has a concrete mechanism in the capability:

- Determinism → `calculate-fp.py` owns the matrix, not the LLM
- Rastreabilidade → `validate-fp-sources.py` blocks orphan functions
- Nao-duplicacao → explicit "regra anti-duplicacao" in Passo 2
- Pergunte-nao-assuma → ambiguity path for both interactive and headless modes

The communication style ("ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF") matches the kind of auditable trace the capability produces. Rare level of persona-tooling mirroring.

### 2. Identity Consistency — **Strong**

The identity is coherent across SKILL.md: the opening description, Mission, Identity, Communication Style, and Principles all reinforce the same picture — a contractual, IFPUG-faithful, source-cited analyst. No drift, no aspirational claims that the capability fails to support.

### 3. Capability Completeness — **Moderate**

The single capability covers the declared mission (count FP auditably). However, several natural neighbors of FP counting are absent:

- **Review/recontagem of existing contagem** — no path to audit or revise a prior `contagem-detalhada.md`. In practice, metrics managers frequently need to re-count after scope change.
- **Diff/delta between entregas** — TJCE contractual work is usually incremental; a "calcular PF de mudanca entre entrega N-1 e N" path is a visible gap.
- **Estimativa / contagem indicativa (NESMA)** — pre-requirements counting (before user-stories exist) is a common upstream need; the prerequisite check currently stops hard.
- **Export to TJCE's contract format** — `resumo-apf.md` is the exit artifact, but contractual submission typically needs a signed/tabular form (CSV/PDF) not mentioned.

None of these are "glaring" (the agent's scope is honestly narrow), but a TJCE metrics gestor will hit one of them within days.

### 4. Redundancy Detection — **Strong**

No redundancy. A single capability, two complementary scripts, two output artifacts with clearly distinct purposes (detailed catalog vs. executive summary). The Correcao em Garantia fast-path is internal to the capability — correctly not a separate capability.

### 5. External Skill Integration — **Strong**

The agent cleanly defers to `tjce-agent-requirements` when prerequisites are missing, rather than reimplementing requirement elicitation. This is the right boundary: APF is downstream of requirements, and the delegation keeps the agent honest about its scope.

### 6. Capability Granularity — **Strong**

CONTAGEM is at the right level: not split into micro-steps (identify-ALI, identify-AIE, classify-complexity as separate capabilities — which would fragment a single IFPUG workflow), and not inflated into "do anything metric-related". The Garantia fast-path sitting inside CONTAGEM (rather than as its own capability) is a correct call — it is a degenerate case of the same workflow, not a different workflow.

### 7. User Journey Coherence — **Moderate**

Entry point is clear (invocation or `garantia` arg). Exit artifacts are valuable (both detailed and executive). The journey is complete for a single fresh count. Weakness: there is no re-entry point — if the user's artifacts change after a count, the agent has no "atualizar contagem" mode. Users will either re-run from scratch (losing the audit trail of what changed) or edit artifacts manually.

## Per-Capability Cohesion

### CONTAGEM — Contagem Detalhada APF

Fits the identity perfectly. A deterministic IFPUG analyst would naturally have exactly this capability, structured exactly this way (inventory → data functions → transactional functions → script-based classification → source validation → VAF → artifacts). The Passo 1–7 structure mirrors standard IFPUG counting procedure. The Garantia fast-path as an internal branch is idiomatic for TJCE contractual reality. No misalignment.

One small friction: Passo 6 (VAF / TDI) asks the user to evaluate 14 characteristics interactively, but no reference material / checklist for the 14 GSCs is attached. A deterministic-obsessed analyst would likely provide the TDI elicitation table inline or as a `references/gsc-checklist.md`.

## Key Findings

### Finding 1 — Missing recontagem / update path
- **Severity:** medium
- **Area:** Capability completeness, User journey
- **What's off:** No supported way to update a prior count when requirements change. The agent will either overwrite silently or require manual diffing.
- **Improvement:** Add a `RECONTAGEM` sub-route (or arg `--update`) that reads the prior `contagem-detalhada.md`, marks functions as novas/alteradas/removidas, and produces a delta summary. Fits the "rastreabilidade" principle naturally.

### Finding 2 — No GSC/TDI elicitation reference
- **Severity:** low
- **Area:** Persona-capability alignment (determinism principle)
- **What's off:** Passo 6 requires the 14 IFPUG General System Characteristics scores but provides no inline definition. An analyst claiming determinism should never leave the user (or itself) guessing which characteristic is which.
- **Improvement:** Add `references/gsc-14-characteristics.md` with each GSC, its IFPUG description, and scoring scale 0–5. Have the capability load it in Passo 6.

### Finding 3 — Headless ambiguity handling may silently under-count
- **Severity:** low
- **Area:** Principle fidelity
- **What's off:** In headless mode, functions with unresolvable DER/RLR/ALR are marked PENDENTE and exit 1 — good. But nothing in the headless contract prevents a downstream consumer from treating exit-1 output as the final count. The JSON summary should surface `pending_count` at top level (already implied — make it explicit and contractual).
- **Improvement:** In SKILL.md headless contract, state that `--json` output always includes `pending_count` and that `total_pf_brutos` excludes pending functions, with an explicit `pf_at_risk` field for their potential contribution.

### Finding 4 — No export to contractual submission format
- **Severity:** suggestion
- **Area:** Capability completeness
- **What's off:** TJCE metrics governance typically requires a signed tabular submission (often XLSX or PDF with standard headers). Markdown `resumo-apf.md` is great for review but may not satisfy contractual handoff.
- **Improvement:** Add a `--export {xlsx|pdf|csv}` option or a small `scripts/export-submission.py` that renders the two MD artifacts into the TJCE contract template.

### Finding 5 — Indicative/early-stage counting gap
- **Severity:** suggestion
- **Area:** Capability completeness
- **What's off:** The prerequisite check blocks counting when user-stories/business-rules don't exist. But NESMA-style indicative counting (7 × #ALI + 35 × #AIE) is a legitimate early-phase practice.
- **Improvement:** Optional `INDICATIVA` capability gated behind a clear disclaimer about precision loss, useful for pre-contract estimation.

## Strengths

- **Persona-tool mirror:** The persona's insistence on determinism is not just text — it is enforced by delegating classification to `calculate-fp.py`. Few agents commit this cleanly.
- **Clear scope boundary:** Deferring requirement artifacts to `tjce-agent-requirements` instead of re-implementing is disciplined agent composition.
- **Source-validation as a hard gate:** `validate-fp-sources.py` operationalizes "rastreabilidade total" — no orphan functions slip through.
- **Garantia fast-path:** A realistic TJCE contractual shortcut handled inline rather than as a separate agent — excellent modeling of the domain.
- **Headless contract:** Explicit exit codes, explicit ambiguity handling, explicit JSON schema. This is a production-quality headless design.
- **Communication style:** The example trace ("ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF") shows the agent is designed for auditability, not for sounding smart.

## Creative Suggestions

1. **Matriz visible mode:** When presenting a complexity classification, have the agent optionally render the IFPUG matrix cell it landed in (e.g., a 3×3 mini-table with the hit cell marked). Visual reinforcement of determinism.
2. **Contract gate integration:** A `--gate` mode that produces a one-line verdict like `APF_COUNT_OK: 312 PF ajustado, 0 pendentes, 0 orfas` suitable for CI / contract-review hooks.
3. **Historical benchmark:** If TJCE has historical PF/prazo data, the agent's parecer could include "entregas comparaveis do TJCE ficaram entre X e Y PF" to help the gestor sanity-check.
4. **Garantia provenance check:** When registering a Correcao em Garantia, optionally validate that the referenced US/RN actually existed in a prior count — prevents abuse of the PF=0 path.
5. **Counting sessions memory:** A lightweight session log (`{output_folder}/apf/.history/`) of prior counts so RECONTAGEM has real material to diff against.

## Final Verdict

This is one of the more coherent single-purpose agents one could review: the persona is uncompromising, the capability is exactly scoped, the tooling enforces the principles, and the boundary with neighboring agents is cleanly drawn. The improvement opportunities are additive (recontagem, export, GSC reference) rather than corrective — there is nothing to fix in what exists, only things to add when the domain demands them.
