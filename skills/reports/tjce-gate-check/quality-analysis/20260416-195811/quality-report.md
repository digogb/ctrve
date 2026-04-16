# Quality Analysis Report: tjce-gate-check

**Skill:** `skills/tjce-gate-check`
**Date:** 2026-04-16
**Scanners:** 6 (L1 Workflow Integrity, L2 Prompt Craft, L3 Execution Efficiency, L4 Skill Cohesion, L5 Enhancement Opportunities, L6 Script Opportunities)
**Lint scripts:** path-standards (pass), scripts (warning — uv not installed)

---

## Overall Grade: Good

This is a well-architected gate-check skill with the strongest script coverage in the TJCE skill suite. Four Python scripts handle all deterministic validation (artifact existence, cross-reference consistency, placeholder detection, score calculation) while the LLM is correctly limited to the two tasks requiring judgment: test case quality assessment and narrative report generation. The 8-step pipeline has proper fail-fast semantics, explicit parallelism, and a clean headless/interactive duality. At 1,226 tokens for an 8-step workflow with dual execution modes, the prompt is lean and purposeful.

However, three structural issues prevent an Excellent rating: (1) a scoring integrity flaw where a missing LLM quality assessment silently inflates the score instead of penalizing it, (2) implicit pipeline plumbing between scripts and the scoring engine that relies on the LLM to infer file routing, and (3) false-positive risk from the `pendente` placeholder pattern in the judicial domain where that word appears constantly in legitimate business rules.

---

## Themes

### Theme 1 — Implicit Contracts and Missing Schemas

**Root cause:** The skill defines script inputs/outputs by convention rather than explicit contract.

Multiple scanners independently flagged the same structural gap: the pipeline between Steps 1-3 and Step 5 relies on implicit naming conventions that are never formally documented.

- **L1 (Workflow Integrity):** `quality-findings.json` is produced by Step 4 but missing from the Output Artifacts table. Consumers cannot discover this artifact from the contract.
- **L2 (Prompt Craft):** Step 4 instructs the LLM to produce findings in a "standard format" without defining the schema. Output will vary across invocations.
- **L4 (Cohesion):** SKILL.md invocations in Steps 1-3 do not include `-o` output paths, but `calculate-gate-score.py` expects specific filenames in `reports/`. The LLM must infer the file routing.
- **L4 (Cohesion):** `quality-findings.json` has no schema contract — the LLM might produce different field names than what the scoring script expects.
- **L5 (Enhancement):** Automators must read Python source to understand verdict.json structure. No JSON Schema is published.
- **L6 (Scripts):** The orchestration plumbing (running scripts, saving outputs to correct files, checking exit codes) is deterministic work the LLM handles via inference.

**Impact:** Medium-High. In headless/CI contexts, implicit contracts create fragile pipelines. A schema drift between the LLM's quality-findings output and the scoring script's expectations would silently produce wrong scores.

### Theme 2 — Scoring Integrity and Degraded Mode Gaps

**Root cause:** The scoring model assumes all inputs are always present and well-formed.

- **L5 (Enhancement) H1:** When `quality-findings.json` is absent (LLM timeout, unavailability, or skipped step), the quality layer receives 0 deductions = perfect 30/30. A project can pass at 100% without any quality assessment running. This is the single most dangerous behavior in the skill.
- **L5 (Enhancement) H3:** Whitespace-only artifact files pass the `st_size > 0` completeness check. A file with only newlines gets full marks.
- **L4 (Cohesion):** Score normalization uses a magic number (divide by 10) with no documented rationale. The cap on deductions per layer may silently limit the impact of accumulated findings.
- **L5 (Enhancement):** No degraded mode behavior is specified for infrastructure failures (LLM down, read-only filesystem, permission errors).

**Impact:** High. The missing-LLM-layer scoring flaw directly undermines the gate's purpose — it protects BUILD phase entry, and a false pass on quality could allow unvalidated specifications through.

### Theme 3 — Domain-Specific False Positives

**Root cause:** Placeholder detection patterns were designed generically, not for the judicial domain.

- **L5 (Enhancement) H2:** The `\bpendente\b` pattern matches legitimate Portuguese judicial text ("recurso pendente de julgamento", "processo pendente de distribuicao", "intimacao pendente"). In TJCE context, this produces persistent false positives that erode trust.
- **L5 (Enhancement) H4:** Duplicate IDs (two business rules sharing the same ID) are silently collapsed by set-based collection, passing through undetected.
- **L5 (Enhancement):** The +/-3 line context window for cross-reference validation is a hidden assumption that produces false negatives on documents with metadata blocks.
- **L4 (Cohesion):** Orphan IDs are documented as "warning" (non-blocking) but scored as "medium" severity with actual score impact — inconsistent semantics.

**Impact:** Medium-High. False positives in the exact domain the tool serves will cause teams to either distort their specification language or lose trust in the checker entirely.

### Theme 4 — Complexity Misclassification and Headless Maturity

**Root cause:** The skill has grown beyond its Simple Workflow classification without updating its infrastructure patterns.

- **L4 (Cohesion):** The skill has 8 steps, 2 execution modes, parallel steps, a human gate with 3-way branching, conditional flags, and multi-agent remediation routing. This is an Orchestrator, not a Simple Workflow.
- **L5 (Enhancement):** Headless maturity scored 7/10 — the LLM dependency in Steps 4 and 6 creates a reliability fault line for CI integration. Two of three output artifacts are non-deterministic.
- **L5 (Enhancement):** No `--continue`/resume support, unlike sibling skills (tjce-verify, tjce-ship). A transient LLM failure requires full pipeline restart.
- **L3 (Efficiency):** The batched parallel invocation intent for Steps 2-3 is correct but the instruction could be more prescriptive to prevent the executing agent from serializing them.
- **L1 (Workflow Integrity):** `verdict.json` vs `gate-check-verdict.json` naming inconsistency in Step 7.

**Impact:** Medium. The misclassification itself is a documentation issue, but the missing orchestrator patterns (state management, resume, degraded mode) create real operational gaps.

### Theme 5 — Remaining LLM Token Optimization

**Root cause:** Two LLM tasks (Steps 4 and 6) contain deterministic sub-work that scripts could handle.

- **L6 (Scripts) Finding 1:** Test case structural pre-analysis (section presence, non-empty expected results, ID references) is fully deterministic. A pre-pass script would reduce LLM workload by ~200-400 tokens and improve consistency.
- **L6 (Scripts) Finding 2:** Report generation contains ~70% structured data (score tables, findings lists, agent mappings) that a template script could produce. In headless mode, the script could replace the LLM entirely.
- **L3 (Efficiency):** Steps 4 and 6 could share LLM context, avoiding re-reading of test cases and redundant inference.
- **L3 (Efficiency):** `validate-cross-references.py` re-reads files and re-splits strings multiple times. `calculate-gate-score.py` iterates findings 9 times.

**Impact:** Low-Medium. The skill is already the best-optimized in the suite. These are incremental improvements totaling ~900-1,700 tokens per invocation. The highest value is in headless mode where scripts could eliminate LLM involvement in Step 6 entirely.

---

## Strengths

1. **Excellent LLM/script boundary.** All deterministic checks (file existence, cross-reference validation, placeholder scanning, score calculation) are offloaded to Python scripts. The LLM handles only subjective quality assessment and prose generation — the ideal division of labor.

2. **Consistent script interfaces.** All 4 scripts share the same CLI pattern (positional output_folder, -o, --verbose), return structured JSON with uniform severity taxonomy, and use proper exit codes. Every script has a corresponding test file.

3. **Fail-fast architecture.** Step 1 blocks immediately on missing artifacts with specific remediation guidance naming the fixing agent. This prevents wasted LLM computation and gives users a direct path to resolution.

4. **Lean token budget.** At 1,226 tokens for an 8-step workflow with two execution modes, the prompt wastes almost nothing. Zero waste patterns detected. Tables are load-bearing, not decorative.

5. **Clean headless/interactive duality.** Each step that behaves differently documents both modes inline. The Headless Contract consolidates machine-readable guarantees (exit codes, output paths, no-prompt policy).

6. **Weighted scoring model with non-negotiables.** The 40/30/30 split prioritizing completeness is defensible. The Inegociaveis section provides unambiguous pass/fail policy. The 90% threshold is aggressive but appropriate for a gate protecting BUILD.

7. **Actionable remediation.** Every finding includes a fix field pointing to a specific TJCE agent or action. The report generation reinforces this by suggesting which agent to invoke, closing the feedback loop.

8. **Explicit parallelism.** Steps 2-3 are correctly identified as independent and marked for parallel execution, giving the agent freedom without over-specifying the mechanism.

9. **Good config resolution pattern.** On Activation loads config with explicit defaults following BMad conventions without over-explaining.

10. **Path standards compliance.** Zero findings from the path standards scanner — all references use correct patterns.

---

## Detailed Analysis

### Structure (L1 — Workflow Integrity)

The skill is structurally sound with well-organized sequential steps, clear fail-fast semantics, and proper headless/interactive mode separation. All four referenced scripts exist on disk with corresponding test files.

**Findings:**
- (Medium) `quality-findings.json` produced by Step 4 is missing from the Output Artifacts table
- (Medium) Step 7 uses `verdict.json` while all other references use `gate-check-verdict.json`
- (Low) Config files referenced in On Activation do not exist in repo; no fallback documented
- (Low) Minor redundancy in parallelism declaration (heading + preamble)

### Craft (L2 — Prompt Craft)

**Verdict: Strong.** The prompt demonstrates good Informed Autonomy — it tells the agent what to validate and when to block but leaves the "how" of quality assessment to the LLM's judgment. The Overview is dense but effective, establishing mission, mode duality, prerequisites, and arguments in 13 lines.

**Findings:**
- (Medium) Missing schema/example for `quality-findings.json` format — the LLM has no anchor for "standard format"
- (Low) Step 6 report guidance is under-specified for consistent cross-run formatting
- (Low) `quality-findings.json` output path ambiguity (not in Output Artifacts table)
- (Negligible) Inegociaveis duplicates Execution Flow constraints — deliberate reinforcement, correctly kept

**Anti-patterns:** None detected. No scripted execution, no LLM doing deterministic work, no token-heavy examples, no redundant preamble.

### Efficiency (L3 — Execution Efficiency)

The pipeline has correct fail-fast placement and explicit parallelization. The dependency chain is a clean DAG with no cycles.

**Findings:**
- (Medium) Steps 4 and 6 could share LLM context to avoid re-reading and re-reasoning
- (Medium) Step 4 LLM assessment does not overlap with Step 5 input pre-staging
- (Low) Steps 2-3 parallelism instruction could be more prescriptive (batched tool calls)
- (Low) `validate-cross-references.py` re-reads files and repeats string splits
- (Low) `calculate-gate-score.py` iterates findings list 9 times instead of single-pass

**Already efficient:** Fail-fast placement (Step 1), deterministic script offloading, Steps 2-3 independence, uniform script output format, headless mode skipping human gate, purely deterministic score calculation, clean dependency DAG.

### Cohesion (L4 — Skill Cohesion)

Purpose alignment is strong — every script and step directly serves the gate-check mission with no scope creep. However, the skill's complexity has outgrown its Simple Workflow classification.

**Findings:**
- (High) Findings file pipeline is implicit — SKILL.md invocations lack `-o` paths but scoring script expects specific filenames
- (Medium) Simple Workflow classification is wrong — should be Orchestrator
- (Medium) Placeholder fail semantics in Inegociaveis are misleading (says "falha" but behavior is score-based, not immediate-block)
- (Medium) `quality-findings.json` has no schema contract
- (Low) Score normalization magic number (divide by 10) undocumented
- (Low) Orphan ID severity mismatch — documented as "warning" but scored as "medium"

### Experience (L5 — Enhancement Opportunities)

User journey analysis across 6 archetypes revealed strong patterns for first-timers (fail-fast with agent remediation) and experts (headless mode), but gaps in progress visibility, error explanation, and infrastructure resilience.

**Key gaps by archetype:**
- First-timer: No orientation on expected directory structure, no progress indicators, score lacks effort context
- Expert: No `--quiet`/`--summary-only`, no diff-from-last-run, no partial re-run
- Confused: Severity-to-blocking mapping is hidden, orphan ID messages lack explanation
- Automator: No JSON Schema published, `--task-type` not required in headless, no resume support

**Headless maturity: 7/10** — Strong CLI args and exit codes, but LLM dependency in Steps 4/6 undermines reliability. Recommended: two-tier headless model (Tier 1 deterministic-only, Tier 2 full with LLM).

### Scripts (L6 — Script Opportunities)

This skill has the strongest script coverage analyzed. Four scripts cover all deterministic operations with consistent JSON contracts, exit codes, and test coverage. Remaining LLM usage is well-targeted.

**Opportunities:**
- (Medium) Test case structural pre-analysis script — reduce LLM workload by ~200-400 tokens
- (Medium) Report generation template script — enable fully scripted headless reports
- (Low) Pipeline orchestrator script — reduce tool calls from 3+ to 1
- (Low) Clarify headless Step 7 is a no-op (already handled by scoring script)

**Total estimated LLM tax on deterministic work:** ~900-1,700 tokens per invocation; up to 2,700 in headless mode.

---

## Recommendations

### Rank 1 — Fix scoring integrity for missing quality layer
**Impact:** Critical | **Effort:** Low
When `quality-findings.json` is absent, set quality layer score to 0 (not 30/30). Add a "quality layer not evaluated" warning to the verdict. This is the single highest-impact fix — it closes a path where specifications pass the gate without any quality assessment.
*Resolves: Theme 2 (scoring integrity), L5 H1*

### Rank 2 — Define explicit findings schema
**Impact:** High | **Effort:** Low
Add a 3-5 line JSON example in SKILL.md showing the expected finding shape `{severity, category, location, issue, fix}`, or create `scripts/findings-schema.json`. Update Step 4 to reference it. Add `quality-findings.json` to the Output Artifacts table.
*Resolves: Theme 1 (implicit contracts), L2 Finding 1, L4 Finding 4, L1 Finding 1*

### Rank 3 — Fix `pendente` false positive pattern
**Impact:** High | **Effort:** Low
Replace bare `\bpendente\b` with context-aware patterns: `\[pendente\]`, `pendente:`, or `status: pendente`. Only flag when it appears in isolation (table cell, standalone line), not embedded in sentences describing legitimate judicial processes.
*Resolves: Theme 3 (domain false positives), L5 H2*

### Rank 4 — Make findings file pipeline explicit
**Impact:** Medium | **Effort:** Low
Update SKILL.md invocation examples to include `-o` output paths. Add a "File Contract" subsection documenting intermediate artifacts and their expected locations. Fix `verdict.json` to `gate-check-verdict.json` in Step 7.
*Resolves: Theme 1 (implicit contracts), L4 Finding 1, L1 Finding 2*

### Rank 5 — Add whitespace-only file detection and duplicate ID detection
**Impact:** Medium | **Effort:** Low
Add content-substantiveness check (strip whitespace, verify length > 50 chars). Track ID definition counts and flag duplicates as high severity.
*Resolves: Theme 2 (scoring integrity), Theme 3 (false positives), L5 H3, L5 H4*

### Rank 6 — Create test case structural pre-analysis script
**Impact:** Medium | **Effort:** Moderate
Create `scripts/pre-analyze-test-cases.py` that parses CT blocks, validates required sections, and produces a filtered input for the LLM. Reduces LLM token spend by ~200-400 tokens and improves consistency.
*Resolves: Theme 5 (token optimization), L6 Finding 1*

### Rank 7 — Align orphan ID severity with documented semantics
**Impact:** Low | **Effort:** Trivial
Either change orphan-id severity to "low" (matching "warning" semantics) or update Inegociaveis to say "IDs orfaos = penalidade leve (medium)". Reword placeholder falha to "score FAIL (via critical finding)".
*Resolves: Theme 3 (domain), L4 Finding 6, L4 Finding 3*

### Rank 8 — Create report generation template script
**Impact:** Medium | **Effort:** Moderate
Create `scripts/generate-report-skeleton.py` for structured report sections. In headless mode, produce the complete report without LLM. In interactive mode, produce skeleton with narrative markers for LLM.
*Resolves: Theme 5 (token optimization), Theme 4 (headless maturity), L6 Finding 2*

### Rank 9 — Reclassify as Orchestrator Workflow
**Impact:** Low | **Effort:** Trivial
Update frontmatter or documentation to reflect the skill's actual complexity level. Consider adopting orchestrator template patterns (state management, resume capability).
*Resolves: Theme 4 (complexity misclassification), L4 Finding 2*

### Rank 10 — Enhance headless resilience (timeout, degraded mode, resume)
**Impact:** Medium | **Effort:** High
Specify LLM timeout for Steps 4/6. Define degraded-mode behavior. Add `--continue` support. Make `--task-type` required in headless mode. Consider two-tier headless model.
*Resolves: Theme 4 (headless maturity), L5 Automator gaps*

---

*Report generated from 6 scanner outputs, 2 lint scripts, and 3 pre-pass metrics. All findings cross-referenced across dimensions for theme identification.*
