# Quality Analysis Report: tjce-verify

**Skill:** `skills/tjce-verify/`
**Date:** 2026-04-16
**Grade:** Good
**Scanners:** 8 (path-standards lint, scripts lint, workflow-integrity prepass, prompt-metrics prepass, execution-deps prepass, L1-L4 LLM scanners, L5 enhancement, L6 script opportunities)

---

## Assessment

`tjce-verify` is a well-architected 4-layer verification orchestrator that cleanly separates orchestration from execution, delegates to `tjce-agent-qa` and deterministic Python scripts, and implements robust headless/interactive modes with well-defined exit codes. The skill has zero critical structural defects. The prepass-reported critical (missing stage file `1-automated.md`) was a false positive -- the skill uses a `references/` routing pattern, and all referenced files exist. The primary areas for improvement are: (1) a data pipeline gap where the LLM performs ~2,000 tokens of deterministic JSON-to-markdown formatting that scripts should handle, (2) missing error recovery for infrastructure failures, and (3) stage/layer numbering inconsistencies that could confuse the model during orchestration.

---

## What's Broken

Nothing is critically broken. The prepass scanner's only critical finding was a false positive (dismissed by L1 analysis). However, one latent integrity risk warrants immediate attention:

**Coverage Null-Pass Bug** (`consolidate-results.py`) -- When `extract_coverage()` cannot parse a coverage percentage from the layer 1 report, it returns `None`. The `determine_verdict()` function treats `None` as "not below threshold" (passes), which directly contradicts the non-negotiable rule: "Cobertura abaixo de {coverage_threshold}% = bloqueio automatico." A malformed report silently bypasses the coverage gate. Single-line fix: treat `None` as NO-GO.

---

## Opportunities (Themed by Root Cause)

### Theme 1: Structured Data Pipeline Gap (resolves 8 findings)

The skill's scripts produce structured JSON, but the LLM is used as a template engine to convert that JSON into markdown reports. This creates ~2,000 tokens of deterministic work per run, introduces regex-parsing brittleness in consolidation, and enables the coverage null-pass bug.

**Findings resolved:**
- Security report markdown assembly (L6-F4, high) -- LLM merges two JSON outputs into markdown
- Verify summary markdown formatting (L6-F5, high) -- LLM templates JSON into markdown
- Consolidation regex parsing of markdown (L3-F8, medium) -- Script re-parses markdown it should consume as JSON
- Coverage re-parsing at Stage 2 (L6-F1, medium) -- Same extraction done by consolidation script
- Layer 1 report formatting (L6-F6, medium) -- Structured data formatted as markdown by LLM
- Coverage null-pass (L4/L5, latent) -- Missing None-guard in verdict logic
- Config note duplication across references (L2-F01, medium) -- 90 tokens of redundant explanation
- Cycle report completeness validation (L6-F3, medium) -- 70% deterministic cross-referencing

**Fix:** Create `format-security-report.py`, extend `consolidate-results.py` with `--format markdown`, expose `extract_coverage()` as CLI subcommand. Add `coverage is None` guard to verdict logic.

### Theme 2: Missing Error Recovery Layer (resolves 5 findings)

The skill does not distinguish between "verification found problems" and "a tool crashed." Script failures, agent unavailability, and infrastructure issues all manifest as ambiguous exit code 1 or undefined behavior.

**Findings resolved:**
- No error recovery for agent invocation failure (L4-F2, moderate)
- Security report format contract undocumented (L4-F4, moderate)
- Script failure indistinguishable from findings (L5, moderate)
- No pre-flight check for runtime dependencies (L5, moderate)
- Stale cycle report pickup (L5, low)

**Fix:** Validate JSON output presence as primary signal (missing JSON = tool failure, not verification result). Add pre-flight check for Python, script executability, agent availability. Tag artifacts with run-ID.

### Theme 3: Naming and Numbering Inconsistency (resolves 4 findings)

The skill uses both "Stage 1-6" and "Camada 1-4" numbering systems that collide (Stage 4 is security, Camada 4 is human gate). The Output Artifacts table misattributes producers to layers.

**Findings resolved:**
- Output Artifacts table layer mismatch (L1-F2, medium)
- Stage/Camada numbering collision in SKILL.md table (L2-F06, medium)
- Dual numbering confusion (L4-F1, low)
- Unused `{user_name}` variable (L1-F1, medium)

**Fix:** Rename the "Camada" column in the Execution Flow table to "Descricao" (it contains descriptions, not layer numbers). Align the Output Artifacts table with the actual 4-layer model. Wire `{user_name}` into the APROVADO action or remove it.

### Theme 4: Parallelism Not Leveraged (resolves 2 findings)

Stages 3 (functional) and 4 (security) are independent but run sequentially. The security scripts are documented as parallelizable but invoked sequentially.

**Findings resolved:**
- Stages 3+4 sequential but independent (L3-F1, medium)
- Security scripts not batched as parallel calls (L3-F2, medium)

**Fix:** Add explicit parallel execution instructions for Stages 3+4. Provide parallel invocation syntax for security scripts.

### Theme 5: UX and Resilience Gaps (resolves 5+ findings)

No first-timer orientation, no state persistence between reference file loads, no progress indicators, no resume capability, no structured JSON verdict for automation.

**Findings resolved:**
- No orientation for first-time users (L5)
- No state persistence across context compaction (L5)
- No progress indicators in headless mode (L5)
- No JSON verdict artifact for automation (L5)
- No `--continue` flag for human gate resume (L5)

**Fix:** Add intent-before-ingestion preamble. Introduce `verify-state.json` for state checkpointing. Surface consolidation JSON as `verify-verdict.json`.

---

## Strengths

1. **Clean orchestrator identity.** The skill explicitly states it "nao executa testes nem faz code review -- ele orquestra." This boundary is enforced consistently: test execution is delegated to `tjce-agent-qa`, security scanning to Python scripts, and the orchestrator focuses on gating and consolidation.

2. **Robust headless contract.** Three distinct exit codes (0/1/2) with well-defined semantics, explicit behavior at every interaction point, and a clear "never automate human gate" invariant. CI/CD integration is straightforward.

3. **Exemplary progressive disclosure.** SKILL.md is ~843 tokens. Reference files load on-demand as stages progress. Only the relevant stage occupies the context window. This is the gold standard for multi-stage orchestration.

4. **Compaction-resilient architecture.** The Inegociaveis section provides a compaction-survival anchor with maximum signal density. Bold formatting, one rule per line, critical rules survive even aggressive summarization.

5. **Deterministic scripts with consistent contracts.** All 4 Python scripts follow a uniform pattern: JSON output, exit code discipline (0=pass, 1=fail), `--output`/`--verbose` flags, and unit tests. The scripts are the most mature component of the skill.

6. **Graduated blocking strategy.** Three distinct blocking points at different boundaries: pre-check (missing artifacts), coverage gate (metrics), and security gate (critical findings). Non-critical findings flow through to consolidation, maximizing information for the PO.

7. **No waste patterns.** Zero instances of "make sure", "remember to", "you should", "please", or other defensive language across all files. The tone is directive and clean throughout.

---

## Detailed Analysis

### Structure (L1 -- Workflow Integrity)

**Status: Pass with minor findings.**

All structural requirements are met: frontmatter is correct, required sections are present, config integration works, headless contract is specified, progression signals exist in all references. The prepass critical (missing `1-automated.md`) was a false positive -- the skill uses `references/` routing, not numbered stage files.

Two medium findings: unused `{user_name}` variable declared in On Activation but never consumed, and Output Artifacts table layer numbering that does not match the 4-layer model described in the Overview.

Three low findings: ASCII-only section title "Inegociaveis" (consistent with project convention), and two reference files listing unused config variables in their config notes.

### Craft (L2 -- Prompt Craft)

**Status: Strong.**

The skill demonstrates excellent prompt craft. Total prompt surface is 241 lines across 4 files -- well within budget for a 6-stage workflow. Progressive disclosure is textbook. Delegation boundaries are marked with "do not duplicate" instructions placed at the exact cognitive risk points. No waste patterns detected.

Two medium findings: config note duplication across all three references (~90 tokens wasted), and stage/camada numbering collision between SKILL.md table and reference file internal labels.

Two low findings: headless exit-code semantics stated in three locations (borderline intentional for compaction survival), and missing terminal progression signal in the last reference file.

### Cohesion (L4 -- Skill Cohesion)

**Status: Strong overall, Moderate on Gap & Redundancy and External Skill Integration.**

Stage flow is coherent, purpose alignment is strong, complexity is appropriate for the domain. Two moderate-severity gaps: no error recovery for `tjce-agent-qa` invocation failure (as opposed to NO-GO results), and no documented format contract for `security-report.md` which the consolidation script must parse with regex.

### Efficiency (L3 -- Execution Efficiency)

**Status: Good, with 25-40% wall-clock optimization possible.**

The design is intentionally sequential for pipeline correctness, with correct fail-fast ordering (cheap pre-checks before expensive operations). Three concrete optimizations: parallelize Stages 3+4 (saves 15-30s), batch security scripts (saves 2-5s), and switch to JSON sidecar pipeline (eliminates regex brittleness).

### Experience (L5 -- Enhancement Opportunities)

**Status: Advisory -- nothing broken, significant opportunity.**

User journey analysis across 6 archetypes reveals high entry friction for first-timers, no delta awareness on re-runs, no state persistence, and a "human gate island" where headless cannot hand off to interactive. The coverage null-pass is the most consequential finding: a non-negotiable gate can be silently bypassed by malformed input.

### Scripts (L6 -- Script Opportunities)

**Status: Excellent existing foundation, ~2,000 tokens of deterministic LLM work to extract.**

Existing scripts are mature with consistent contracts, JSON output, and unit tests. Six script opportunities identified, with the two highest-value being security report assembly (500-800 tokens, 100% deterministic) and verify summary formatting (500-700 tokens, ~90% deterministic). These two alone account for over half the total deterministic token tax.

---

## Recommendations (Ranked by Impact)

| Rank | Action | Resolves | Effort |
| ---- | ------ | -------- | ------ |
| 1 | Fix coverage null-pass: treat `None` as NO-GO in `consolidate-results.py` | Latent integrity risk, 1 finding | Low (single-line fix) |
| 2 | Create `format-security-report.py` to replace LLM JSON-to-markdown assembly | Theme 1: 1 high finding, eliminates 500-800 tokens/run | Low (50-line script) |
| 3 | Extend `consolidate-results.py` with `--format markdown` for verify summary | Theme 1: 1 high finding, eliminates 500-700 tokens/run | Low (template addition to existing script) |
| 4 | Align stage/layer numbering in SKILL.md table and Output Artifacts | Theme 3: 4 findings across L1, L2, L4 | Low (table text edits) |
| 5 | Add error recovery: validate JSON output presence, distinguish tool failure from findings | Theme 2: 3 findings across L4, L5 | Medium |
| 6 | Parallelize Stages 3+4 and batch security scripts | Theme 4: 2 medium findings, 25-40% wall-clock savings | Medium |
| 7 | Remove config note duplication from reference files | Theme 1: 1 medium finding, saves ~90 tokens | Low |
| 8 | Add pre-flight check (Stage 0) for runtime dependencies | Theme 2: 2 findings | Medium |
| 9 | Introduce `verify-state.json` for state persistence and compaction resilience | Theme 5: 3 findings | Medium |
| 10 | Surface consolidation JSON as `verify-verdict.json` and add intent-before-ingestion preamble | Theme 5: 2 findings | Low-Medium |

---

## Scanner Summary

| Scanner | Status | Findings |
| ------- | ------ | -------- |
| Path Standards (lint) | Pass | 0 |
| Scripts (lint) | Warning | 4 high (uv not found -- environment issue, not code) |
| Workflow Integrity (prepass) | Fail | 1 critical (false positive -- dismissed by L1) |
| Prompt Metrics (prepass) | Info | 0 issues, baseline metrics collected |
| Execution Deps (prepass) | Pass | 0 (empty graph -- semantic analysis done by L3) |
| L1 Workflow Integrity | Pass | 2 medium, 3 low |
| L2 Prompt Craft | Strong | 2 medium, 2 low |
| L3 Execution Efficiency | Good | 3 medium, 3 low (2 informational) |
| L4 Skill Cohesion | Strong | 2 moderate, 1 low |
| L5 Enhancement Opportunities | Advisory | 5 experience gaps, 4 delight opportunities, 6 edge cases |
| L6 Script Opportunities | Advisory | 2 high, 3 medium, 1 low (deterministic token savings) |
