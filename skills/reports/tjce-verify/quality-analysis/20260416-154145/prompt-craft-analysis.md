# Prompt Craft Analysis — tjce-verify

**Skill:** `skills/tjce-verify/`
**Date:** 2026-04-16
**Analyzer:** PromptCraftBot
**Pre-pass data:** `prompt-metrics-prepass.json`

---

## Assessment

**Overall grade: STRONG**

This is a well-architected orchestration skill. SKILL.md is compact (69 lines, ~843 tokens), establishes clear mission boundaries, and delegates execution to three progressively-loaded reference files. The total prompt surface across all four files is 241 lines — well within the ~500 line budget for a multi-stage orchestration workflow. The skill demonstrates strong prompt craft fundamentals with a few medium-severity improvement opportunities.

---

## Prompt Health Summary

| Metric | Value | Status |
| ------ | ----- | ------ |
| SKILL.md lines | 69 | Excellent — lean orchestrator |
| SKILL.md tokens | ~843 | Well within budget |
| Total lines (all files) | 241 | Good for a 6-stage workflow |
| Reference files | 3 | Matches 3 stage-pairs |
| Progressive disclosure | Yes — via reference loading | Core design strength |
| Config header (SKILL.md) | Yes (frontmatter) | Correct |
| Config headers (references) | Yes (frontmatter) | Correct |
| Progression signals | Present in all 3 references | Correct |
| Waste patterns (prepass) | 0 | Clean |
| Back references (prepass) | 0 | Clean |

---

## Key Findings

### F-01: Config note duplication across all three references

- **Severity:** Medium
- **Files:** `references/pre-check-and-automated.md:6`, `references/functional-and-security.md:6`, `references/consolidation-and-gate.md:6`
- **Issue:** Each reference file opens with a nearly identical "Config note" line explaining that variables are resolved by SKILL.md at activation time. This is stated three times using slightly different variable lists (one omits `{coverage_threshold}`). The information is already implicit from SKILL.md's "On Activation" section, which resolves these variables before any reference is loaded.
- **Token cost:** ~90 tokens across 3 files
- **Fix:** Remove all three "Config note" lines. SKILL.md's "On Activation" section already establishes variable resolution. The reference files receive these variables as resolved values — they do not need to explain the resolution mechanism. If the variable list divergence (missing `{coverage_threshold}` in functional-and-security.md) is intentional, encode that constraint in SKILL.md's config table instead.

### F-02: Headless exit-code semantics stated in three locations

- **Severity:** Low
- **Files:** `SKILL.md:14`, `SKILL.md:47`, `SKILL.md:53-57`
- **Issue:** The headless exit-code contract is conveyed in the Overview (line 14: "Para no gate humano com exit 2"), in Inegociaveis (line 47: "em headless, gera artefato e para (exit 2)"), and fully specified in the Headless Contract section (lines 53-57). The Overview and Inegociaveis mentions are partially redundant with the dedicated section.
- **Why this is Low not Medium:** The Inegociaveis section serves as a compaction-survival anchor — if context is compressed, these rules survive. The Overview mention provides quick-scan affordance. Both serve legitimate prompt craft purposes. The redundancy is borderline intentional.
- **Fix (optional):** In the Overview, change to `--headless` / `-H` para execucao sem interacao` (drop the exit-code detail). In Inegociaveis, keep the rule but drop the implementation detail: "Homologacao humana nunca automatizada — em headless, gera artefato e para". Leave the Headless Contract section as the single source of exit-code semantics.

### F-03: "Do not duplicate/replicate" instructions are well-placed domain framing, not waste

- **Severity:** N/A (false positive prevention)
- **Files:** `references/pre-check-and-automated.md:36`, `references/functional-and-security.md:14`
- **Issue (non-issue):** Lines like "delegate, do not duplicate" and "Do not replicate this logic" could be flagged as defensive padding. They are NOT waste. These are critical orchestration boundaries — the skill delegates to `tjce-agent-qa` and the most common failure mode for an orchestrator is reimplementing delegated logic. This is intelligence placement: the instruction sits directly next to the delegation point where the model is most likely to drift.
- **Verdict:** Keep as-is. This is theory-of-mind-informed prompt craft.

### F-04: Missing explicit progression signal in consolidation-and-gate.md

- **Severity:** Low
- **Files:** `references/consolidation-and-gate.md` (end of file)
- **Issue:** The first two reference files end with explicit `**Progression:** If PASS/not blocked, load references/next-file.md` signals. The third reference file (consolidation-and-gate.md) has no such closing signal because it is the terminal stage. While logically correct, the absence breaks the pattern. A terminal signal like "**Progression:** Workflow complete. No further stages." would maintain structural consistency and make the terminal condition explicit for the model.
- **Fix:** Add a closing line: `**Progression:** Workflow complete. Final status determined by PO decision (interactive) or AGUARDANDO HOMOLOGACAO artifact (headless).`

### F-05: Inegociaveis section is excellent compaction-survival design

- **Severity:** N/A (strength)
- **File:** `SKILL.md:42-48`
- **Issue (non-issue):** The Inegociaveis section appears to duplicate rules stated elsewhere (coverage gate, security gate, human gate). This is intentional and correct. In a compaction event, SKILL.md may be summarized and reference files dropped. The Inegociaveis section ensures the non-negotiable rules survive compression. Each rule is one line with bold formatting — maximum signal density.
- **Verdict:** Keep as-is. This is the correct pattern for compaction-critical rules.

### F-06: Stage numbering mismatch between SKILL.md table and reference content

- **Severity:** Medium
- **Files:** `SKILL.md:34-38` vs reference file stage numbers
- **Issue:** SKILL.md's Execution Flow table numbers stages as 1-2, 3-4, 5-6 but maps them to "Camada" values that are different (Pre-check + Automatizada, Funcional + Seguranca, Consolidacao + Gate). Inside the reference files, the actual stage identifiers are: Stage 1 (Pre-Check), Stage 2 (Camada 1), Stage 3 (Camada 2), Stage 4 (Camada 3), Stage 5 (Consolidacao), Stage 6 (Gate Humano). The "Camada" column in the SKILL.md table does not match the "Camada N" labels used inside the references ("Camada 1: Verificacao Automatizada" is Stage 2, not Stage 1). This creates a numbering collision that could confuse the model during orchestration.
- **Fix:** Align the SKILL.md table to use the same stage/camada numbering as the reference files, or remove the "Camada" column and rely on descriptive names only. The simplest fix: rename the SKILL.md table column from "Camada" to "Descricao" since it contains descriptions, not camada numbers.

---

## Strengths

1. **Exemplary progressive disclosure.** SKILL.md is a pure orchestrator (~843 tokens) that loads stage-specific context on demand. This is the gold standard for multi-stage workflows — only the relevant stage occupies the context window at execution time.

2. **Outcome-oriented stage definitions.** Each stage in the references specifies WHAT to produce and WHEN to block, not HOW to implement the logic. Script invocations are concrete commands (good), and the orchestration steps are numbered but not over-specified.

3. **Clean delegation boundaries.** The skill explicitly marks what `tjce-agent-qa` handles vs. what the orchestrator handles. "Do not duplicate" instructions are placed at the exact cognitive risk points.

4. **Compaction-resilient architecture.** The Inegociaveis section, the frontmatter config headers, and the progression signals in each reference file create a robust survival skeleton. If the context window compresses, the critical rules and flow control survive.

5. **No waste patterns detected.** Zero instances of "make sure", "remember to", "you should", "please", or other defensive/supplicant language. The tone is directive and clean throughout.

6. **Appropriate headless contract.** Exit codes, output locations, and behavioral differences are specified in a single dedicated section with a clean table format.

7. **Script-backed determinism.** Security scans and consolidation are delegated to Python scripts rather than described as LLM reasoning tasks. This is architecturally sound — deterministic operations should not rely on stochastic reasoning.

---

## Summary

The skill is well above average in prompt craft quality. The architecture correctly separates orchestration (SKILL.md) from stage execution (references) with clean progressive disclosure. The two medium-severity findings (config note duplication, stage numbering mismatch) are straightforward fixes. The low-severity findings are optional polish. No critical or high-severity issues were identified.

| Severity | Count |
| -------- | ----- |
| Critical | 0 |
| High | 0 |
| Medium | 2 (F-01, F-06) |
| Low | 2 (F-02, F-04) |
| Strengths noted | 7 |
