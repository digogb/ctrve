# Skill Cohesion Analysis: tjce-gate-check

**Skill:** `skills/tjce-gate-check`
**Date:** 2026-04-16T19:58:11
**Analyst:** SkillCohesionBot

---

## Assessment

This is a well-architected gate-check skill that cleanly separates deterministic validation (4 Python scripts) from LLM judgment (test quality assessment + report generation). The 3-layer model with weighted scoring is appropriate for the SPEC-to-BUILD transition, and the fail-fast semantics on missing artifacts prevent wasted computation. However, the skill claims to be a Simple Workflow while exhibiting orchestrator-level complexity (parallel steps, dual execution modes, human gate, multi-agent remediation routing), and there is a structural disconnect between how the SKILL.md invokes scripts and how calculate-gate-score.py discovers their output.

---

## Cohesion Dimensions

| Dimension | Rating | Notes |
|---|---|---|
| **Purpose alignment** | **Strong** | Every script and every step directly serves the gate-check mission. No scope creep. |
| **Stage flow coherence** | **Moderate** | The 8-step flow is logical, but the glue between steps is underspecified -- SKILL.md does not show how script outputs get written to `reports/` before calculate-gate-score.py reads them. |
| **Internal consistency** | **Moderate** | Script CLI interfaces are uniform (positional output_folder, -o, --verbose), but SKILL.md invocations in Steps 1-3 do not pass `-o` to write findings files, creating an implicit gap. |
| **Complexity appropriateness** | **Weak** | Labeled as a Simple Workflow, but the dual-mode execution (interactive vs headless), parallel steps, human gate with 3-way decision, and multi-agent remediation routing are orchestrator patterns. Should be classified as an Orchestrator Workflow. |
| **Dependency graph logic** | **Moderate** | Step 1 fail-fast is clear. Steps 2-3 parallel is correct (independent). But Step 4 (LLM quality) has no fail-fast interaction with Step 1 -- if Step 1 blocks, the SKILL.md says stop, but there is no mechanism preventing the LLM from reading artifacts that partially exist. |
| **External skill integration** | **Strong** | Remediation guidance correctly names specific agents (`tjce-agent-requirements`, `tjce-agent-qa capability BUILD`, architecture agent). Fix suggestions are actionable. |
| **Gap & redundancy detection** | **Moderate** | check-placeholders.py partially overlaps with the LLM quality step (Step 4) -- both assess structural quality of test cases. The boundary between "deterministic quality" and "AI quality" needs sharper delineation. |

---

## Key Findings

### Finding 1 -- Findings file pipeline is implicit
- **Severity:** High
- **Area:** Stage flow coherence
- **What is wrong:** SKILL.md Step 1 invokes `check-artifacts-exist.py {output_folder}` without `-o {output_folder}/reports/artifacts-findings.json`. Same for Steps 2-3. But `calculate-gate-score.py` reads from `reports/artifacts-findings.json`, `reports/crossref-findings.json`, `reports/placeholder-findings.json`, and `reports/quality-findings.json`. There is no documented step that bridges script stdout to those files. The LLM agent must infer this, which is fragile.
- **Fix:** Update SKILL.md invocation examples to include explicit `-o` paths, e.g.: `python3 scripts/check-artifacts-exist.py {output_folder} -o {output_folder}/reports/artifacts-findings.json`. Or add a "File Contract" section that declares expected intermediate artifacts.

### Finding 2 -- Simple Workflow classification is wrong
- **Severity:** Medium
- **Area:** Complexity appropriateness
- **What is wrong:** The skill has 8 steps, 2 execution modes, parallel step execution, a human gate with 3-way branching, conditional flags (--data-model, --ux), and remediation routing to external agents. This is an Orchestrator, not a Simple Workflow. Misclassification may cause the framework to apply wrong expectations (e.g., no parallelism support, no state management).
- **Fix:** Reclassify as Orchestrator Workflow. If the framework distinguishes these, adopt the orchestrator template. If not, at minimum document the complexity level in the frontmatter.

### Finding 3 -- check-placeholders.py exit code conflicts with SKILL.md fail-fast semantics
- **Severity:** Medium
- **Area:** Internal consistency
- **What is wrong:** SKILL.md "Inegociaveis" says "Placeholder TODO em qualquer artefato = falha". But check-placeholders.py runs in Step 3 (parallel with cross-refs), and the fail-fast is only at Step 1. A placeholder finding produces exit code 1 from the script but the SKILL.md does not say to halt at Step 3 -- it proceeds to Steps 4-5. The "falha" only materializes at scoring time when calculate-gate-score.py sees the critical finding. This is correct behavior, but the "Inegociaveis" language ("falha") implies immediate blocking like Step 1, which is misleading.
- **Fix:** Reword the Inegociaveis entry for placeholders to: "Placeholder TODO em qualquer artefato = score FAIL (via critical finding)" to distinguish from the immediate-block behavior of missing artifacts.

### Finding 4 -- quality-findings.json has no schema contract
- **Severity:** Medium
- **Area:** Stage flow coherence
- **What is wrong:** Step 4 asks the LLM to "produce a quality-findings.json in the standard format." But the standard format is only implicitly defined by what the other scripts output. There is no schema file or explicit field list. An LLM might produce slightly different field names (e.g., "recommendation" instead of "fix"), causing calculate-gate-score.py to silently miss findings.
- **Fix:** Define the finding schema explicitly in SKILL.md or in a shared schema file. At minimum, document: `{severity: critical|high|medium|low, category: string, location: {file: string, line?: number}, issue: string, fix: string}`.

### Finding 5 -- Score normalization can silently cap deductions
- **Severity:** Low
- **Area:** Dependency graph logic
- **What is wrong:** `calculate-gate-score.py` normalizes deductions per layer with `max_deductions = max_points / 10`. For the completeness layer (40 points), this means max_deductions = 4. With SEVERITY_DEDUCTIONS critical = 1.0, you need 4 critical findings to zero out the layer. But a single missing required artifact already triggers fail-fast in Step 1, so this path is never reached for completeness. The normalization constant (divide by 10) is a magic number with no documented rationale.
- **Fix:** Document the normalization rationale. Consider whether the divisor should be configurable or derived from expected finding counts.

### Finding 6 -- Orphan IDs severity mismatch
- **Severity:** Low
- **Area:** Internal consistency
- **What is wrong:** SKILL.md "Inegociaveis" says "IDs orfaos = warning -- reporta mas nao bloqueia." In validate-cross-references.py, orphan IDs are severity "medium". The CATEGORY_TO_LAYER mapping in calculate-gate-score.py maps "orphan-id" to "cross-reference" layer. Medium severity deducts 0.2 points. So orphans DO contribute to potential failure (if enough accumulate). "Warning" implies zero scoring impact, which is not the case.
- **Fix:** Either change orphan-id severity to "low" (0.0 deduction, matching "warning" semantics) or update the Inegociaveis to say "IDs orfaos = penalidade leve (medium)" so the documentation matches behavior.

---

## Strengths

1. **Clean separation of concerns.** Deterministic validation in Python scripts, judgment calls in LLM steps, scoring in a dedicated aggregator. This is the right architecture for a gate-check -- it makes the deterministic parts testable and reproducible.

2. **Consistent script interfaces.** All 4 scripts share the same CLI pattern (positional output_folder, -o, --verbose), return structured JSON with uniform severity taxonomy, and use proper exit codes. This is genuinely well-engineered.

3. **Fail-fast on missing artifacts.** Step 1 blocking before any further validation is correct and avoids misleading partial scores. The _fix_for() function providing specific agent names is a nice touch for remediation UX.

4. **Dual-mode design.** The headless/interactive split is well thought out. Headless mode produces machine-readable verdict.json with exit codes; interactive mode adds human gate and complementary decisions. This enables CI integration without sacrificing the human-in-the-loop for manual usage.

5. **Weighted scoring model.** The 40/30/30 split prioritizing completeness over cross-references and quality is a defensible choice. The 90% threshold is aggressive but appropriate for a gate that protects the BUILD phase.

6. **Actionable remediation.** Every finding includes a "fix" field pointing to a specific agent or action. The report generation step (Step 6) reinforces this by suggesting which TJCE agent to invoke. This closes the feedback loop.

---

## Creative Suggestions

1. **Add a "dry-run" mode.** Beyond headless and interactive, consider a `--dry-run` that executes all validation but skips writing any output files. Useful for developers who want to check readiness without polluting the reports directory. This would also help during SPEC iterations where the gate is not yet expected to pass.

2. **Introduce a findings schema file.** Create `scripts/findings-schema.json` (JSON Schema) that all scripts validate against before output. The LLM step (Step 4) can reference it as a contract. This eliminates the implicit format coupling and makes the pipeline robust against drift.

3. **Progressive scoring feedback.** Instead of calculating the score only at Step 5, consider having each script emit a partial score alongside its findings. The LLM can then present running totals during interactive mode: "After Layer 1: 40/40. After Layer 2: 35/40+25/30..." This gives the user early signal without waiting for the full pipeline.

4. **Trend tracking.** Store historical verdict.json files with timestamps. After a few gate-check runs, the report could include trend data: "Score improved from 72% to 91% over 3 iterations. Remaining gap: 2 unlinked RNs." This turns the gate-check from a binary pass/fail into a progress tracker.

5. **Gate-check as pre-commit hook.** The headless mode with exit codes is already CI-ready, but consider also documenting a pattern where `check-artifacts-exist.py` alone runs as a lightweight pre-commit check during the SPEC phase. This catches missing artifacts before the author even requests a full gate-check.

6. **Decouple complementary decisions from the gate.** Step 7 (task type, manual flag, data model, APF estimate) collects metadata that is not validation -- it is classification. Moving it to a separate micro-skill or making it a pre-gate step would sharpen the gate-check's single responsibility and allow those decisions to be captured earlier in the workflow (e.g., during SPEC initiation).
