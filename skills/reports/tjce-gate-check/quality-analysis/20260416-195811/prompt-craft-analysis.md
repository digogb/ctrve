# Prompt Craft Analysis — tjce-gate-check

**Skill:** `skills/tjce-gate-check`
**Type:** Simple Workflow (single SKILL.md, no stage files, no references/)
**Date:** 2026-04-16
**Tokens:** ~1,226 (SKILL.md only; scripts are external Python)

---

## Assessment

**Overall Craft Verdict: STRONG**

This is a well-architected gate-check skill that delegates deterministic validation to four external Python scripts while reserving the LLM for the two tasks that genuinely require judgment: test-case quality assessment (Step 4) and narrative report generation (Step 6). The Overview is dense but effective — it establishes mission, execution mode duality, prerequisites, and arguments in 13 lines. The skill demonstrates good Informed Autonomy: it tells the agent *what* to validate and *when* to block, but leaves the "how" of quality assessment and report prose to the LLM's own judgment. At ~1,226 tokens for an 8-step workflow with headless/interactive duality, this is lean and purposeful.

---

## Prompt Health Summary

| Metric | Value | Assessment |
| ------ | ----- | ---------- |
| SKILL.md lines | 117 | Well within budget for a simple workflow |
| Token estimate | 1,226 | Lean — good discipline |
| Sections | 13 | Appropriate granularity for 8 steps + framing |
| Tables | 2 (9 lines) | Load-bearing — decision matrix and artifact registry |
| Fenced blocks | 3 (4 lines) | Minimal, all are actual shell commands |
| Waste patterns detected | 0 | Clean |
| Back-references | 0 | Expected for a self-contained simple workflow |
| Overview lines | 13 | Dense but complete |
| Config header | Present | Correct |
| Progression markers | Present | Steps are clearly sequenced |

---

## Key Findings

### Finding 1 — Missing quality-findings.json format specification

| Field | Value |
| ----- | ----- |
| Severity | **Medium** |
| Location | SKILL.md:55 |
| What | Step 4 instructs the LLM to produce `quality-findings.json` in a "standard format" but never defines that format or points to a schema |
| Why | The LLM has no anchor for what "standard format" means. Without a concrete example or schema reference, output will vary across invocations, which directly undermines the deterministic `calculate-gate-score.py` that must parse it in Step 5 |
| Fix | Add a 3-4 line JSON example inline showing the expected shape `{severity, category, location, issue, fix}`, or reference a JSON Schema file in `scripts/`. This is load-bearing context, not waste |

### Finding 2 — Step 6 report guidance is under-specified for the LLM task

| Field | Value |
| ----- | ----- |
| Severity | **Low** |
| Location | SKILL.md:67 |
| What | Step 6 tells the LLM to generate a report with "per-layer breakdown, all findings, and remediation guidance" but does not specify the report structure (headings, sections) |
| Why | For a gate-check report that a PO/Tech Lead will review (Step 8), consistency in structure across runs matters. The current instruction grants full autonomy on layout, which is appropriate for a first version but may cause drift. This is a trade-off the author likely made deliberately |
| Fix | Optional: add 4-5 lines with expected section headings (e.g., Resumo, Completude, Consistencia, Qualidade, Score, Recomendacoes). Only if consistency across runs is valued |

### Finding 3 — `quality-findings.json` output path ambiguity

| Field | Value |
| ----- | ----- |
| Severity | **Low** |
| Location | SKILL.md:55 |
| What | Step 4 says "in the reports directory" but the Output Artifacts table at line 109 does not list `quality-findings.json` |
| Why | The Output Artifacts table is the agent's contract with downstream consumers. Omitting an artifact the agent produces creates ambiguity about whether it should persist or is ephemeral |
| Fix | Add `quality-findings.json` to the Output Artifacts table with producer "LLM" and step "4" |

### Finding 4 — Inegociaveis duplicates Execution Flow constraints

| Field | Value |
| ----- | ----- |
| Severity | **Negligible** |
| Location | SKILL.md:93-99 |
| What | "Artefato obrigatorio faltando = falha imediata" and "Placeholder TODO = falha" repeat what Steps 1 and 3 already state |
| Why | Arguably load-bearing: the Inegociaveis section serves as a quick-reference contract and reinforcement for the LLM. The duplication is intentional emphasis, not waste. Keeping it is the right call |
| Fix | None — this is deliberate reinforcement |

---

## Strengths

1. **Excellent LLM/script boundary.** The skill correctly offloads all deterministic checks (file existence, cross-reference validation, placeholder scanning, score calculation) to Python scripts and uses the LLM only for subjective quality assessment and prose generation. This is the ideal division of labor — it avoids both the anti-pattern of asking an LLM to count things and the anti-pattern of trying to script qualitative judgment.

2. **Dual-mode design is clean.** The interactive/headless duality is handled without branching spaghetti. Each step that behaves differently states its mode variance inline. The Headless Contract section consolidates the machine-readable guarantees (exit codes, output paths, no-prompt policy) in one place.

3. **Fail-fast architecture.** Step 1 is explicitly marked as fail-fast with a BLOCK instruction, preventing wasted LLM computation on quality assessment when basic prerequisites are missing. This shows awareness of token economics.

4. **Parallelism is declared, not prescribed.** Steps 2-3 are marked as independent and parallel, giving the agent freedom to execute them concurrently without over-specifying the mechanism.

5. **Lean token budget.** At 1,226 tokens for an 8-step workflow with two execution modes, this skill wastes almost nothing. Tables are used for structured data (decisions, artifacts), not decoration. Fenced blocks contain only actual executable commands.

6. **Good config resolution pattern.** The On Activation section loads config with explicit defaults, following the BMad convention without over-explaining it.

---

## Pruning Opportunities

Minimal. This skill is already lean. The only candidate for removal would be the Inegociaveis section (~7 lines), but as noted in Finding 4, it serves as deliberate reinforcement and quick-reference. The token cost is negligible (~50 tokens) and the clarity benefit is real. No pruning recommended.

---

## Anti-Pattern Check

| Anti-Pattern | Present? | Notes |
| ------------ | -------- | ----- |
| Scripted Execution (over-specifying HOW) | No | Steps describe what, scripts handle how |
| LLM doing deterministic work | No | All counting/matching delegated to Python |
| Token-heavy examples | No | Zero inline examples (Finding 1 argues one is needed) |
| Vague outcome criteria | Partially | Step 4 and 6 could be tighter (Findings 1-2) |
| Missing fail-fast | No | Step 1 is explicitly fail-fast |
| Redundant preamble | No | Overview is dense and load-bearing |
