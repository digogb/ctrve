# Agent Cohesion Analysis — tjce-agent-qa

**Date:** 2026-04-16  
**Analyzer:** CohesionBot  
**Skill path:** `skills/tjce-agent-qa/`  
**Files analyzed:** `SKILL.md`, `references/build-capability.md`, `references/verify-capability.md`

---

## Executive Summary

The `tjce-agent-qa` agent is well-structured and internally consistent. The persona, communication style, and operational principles are tightly aligned with both capabilities. No critical cohesion failures were found. Three medium-severity gaps exist (missing test types, a file path inconsistency, and a weak coverage-overlap), plus several low-severity advisory items. The agent is ready for production with minor corrections.

---

## 1. Persona–Capability Alignment

**Assessment: STRONG**

The "QA senior rigoroso e detalhista" identity maps naturally to both BUILD and VERIFY:

- BUILD's hard stance on coverage ≥80% as a blocking gate is a direct expression of the persona's stated intolerance for uncovered code.
- BUILD's code review step requires OWASP Top 10 awareness and architecture judgment — consistent with a senior, not a junior, profile.
- VERIFY's defect classification rules ("when in doubt, escalate severity") and the go/no-go recommendation framework reinforce the no-sugarcoating communication style declared in SKILL.md.
- The "evidence over opinion" principle is operationalized in both capabilities: BUILD mandates file path + line number + code snippet for every code review finding; VERIFY requires reproduction steps + stack trace for every defect.

**Minor observation (low):** SKILL.md states the persona "celebrates high coverage and clean code — briefly." Neither capability prompt includes a positive-acknowledgment step or even a reminder to do so. This is cosmetic but creates a persona gap when the agent silently produces a passing report without celebration.

---

## 2. Capability Completeness

**Assessment: ADEQUATE with gaps**

The two capabilities cover the core QA workflow (design, implement, execute, report). However, for a judicial system context, three test types are absent:

### 2a. No Regression Testing Protocol (medium severity)

Neither capability defines a regression strategy for when a defect from a previous cycle is marked as "corrigido." VERIFY tracks defect status across cycles (novo/reaberto/corrigido) but does not specify how the agent should re-execute or scope a regression pass. A regression run on fixed Alta defects before GO is a QA fundamental — its absence is a gap, not a catastrophic omission, because the user can re-invoke VERIFY manually.

**Recommendation:** Add a "Regression Scope" section to `verify-capability.md` that lists the test cases linked to corrected defects and marks them as regression candidates for the next cycle.

### 2b. No Performance or Load Testing (low severity)

Judicial systems often have SLA requirements under high concurrent load (e.g., during audiencia periods). Neither capability mentions NFR/performance testing. This is advisory only — a lean QA skill reasonably scopes performance testing as out-of-band — but the skill description says "testes e code review" without scoping out performance.

**Recommendation:** Add a parenthetical to the SKILL.md description clarifying that performance and load testing are out of scope for this skill, to prevent user confusion.

### 2c. No Accessibility Testing (low severity)

TJCE systems serve public and judicial staff, including users with accessibility needs. Accessibility (WCAG conformance) is a common audit point. No mention in either capability. Same advisory posture as performance: scope it out explicitly if not intended.

---

## 3. Redundancy Detection — BUILD vs. VERIFY

**Assessment: LOW OVERLAP, one duplicate step**

BUILD and VERIFY share one structural element: both run the coverage tool (`parse-coverage.py`) and write coverage data. BUILD writes to `{output_folder}/reports/coverage-report.md`; VERIFY embeds a "coverage snapshot" inside `test-cycle-N.md`.

This is not technically redundant — BUILD's report is a standalone coverage artifact, while VERIFY's snapshot is contextual within a cycle. The distinction is appropriate. However, both capabilities call the identical bash commands to generate coverage:

```bash
python3 -m pytest --cov --cov-report=term-missing 2>&1
python3 scripts/parse-coverage.py <coverage-output> --threshold 80
```

This creates a mild maintenance coupling: if the coverage command changes (e.g., new flags), it must be updated in two places. Low severity in a two-file skill, but worth noting for future maintenance.

**Recommendation:** Consider extracting the coverage execution block into a shared `references/run-coverage.md` snippet included by both capabilities, or at minimum add a comment noting the duplication.

---

## 4. External Skill Integration — tjce-agent-requirements

**Assessment: WELL INTEGRATED**

The prerequisite check in SKILL.md correctly names the three output artifacts of `tjce-agent-requirements`:

- `{output_folder}/requirements/user-stories.md`
- `{output_folder}/requirements/business-rules.md`
- `{output_folder}/requirements/messages.md`

These match the actual output paths defined in `tjce-agent-requirements/SKILL.md` (default `{output_folder}` = `{project-root}/_bmad-output`). The integration contract is sound.

BUILD additionally re-reads these files at capability start, providing a double-check rather than relying solely on the SKILL.md gate. This is a good defensive pattern.

**One cohesion issue (medium severity):** The prerequisite check in SKILL.md mentions `messages.md`, but the `tjce-agent-requirements` skill produces this as part of its "System Messages" artifact. VERIFY's "Prerequisites Validation" section does not re-check the requirements artifacts — it only checks for test artifacts. This is intentional (VERIFY can work with any test suite), but it creates an asymmetry: if a user invokes VERIFY directly without having run requirements generation, there is no guard against testing against a phantom spec. The soft warning in VERIFY ("inform the user that BUILD should run first, but do not block") is acceptable for test artifacts but doesn't address requirement traceability at all.

**Recommendation:** Add a softer advisory to VERIFY's prerequisites section: "If `{output_folder}/requirements/business-rules.md` is absent, note that defect-to-RN traceability in the cycle report will be incomplete."

---

## 5. Capability Granularity — BUILD's Four Deliverables

**Assessment: APPROPRIATE, with one extraction candidate**

BUILD packages four deliverables sequentially: test cases, unit test code, coverage verification, and code review. This is a reasonable bundling for a "build phase" in a lean agent. However, the code review step stands apart from the other three in a meaningful way:

- Steps 1–3 are constructive (create artifacts, generate code, measure results).
- Step 4 (code review) is evaluative and operates on the application source, not on the test artifacts from steps 1–3.

BUILD itself acknowledges this tension — it explicitly recommends running code review in a clean session and asks the user for confirmation before proceeding in the same session. This recommendation is correct but architecturally awkward: a capability that recommends deferring one of its own four steps is signaling that the step belongs elsewhere.

**Options (advisory, not blocking):**

1. Promote code review to a third capability (REVIEW — Code Review) with its own menu code. This would give it a cleaner entry point and remove the "dirty context" disclaimer.
2. Keep current structure but remove the recommendation to run in a separate session, instead always appending the disclaimer to the report header.

Option 1 produces better user experience (the user can invoke code review independently, without triggering test generation). The current bundling is not wrong, but it underserves users who only need code review.

---

## 6. User Journey Coherence

**Assessment: COHERENT end-to-end, one file path bug**

The canonical user journey works as expected:

1. User runs `tjce-agent-requirements` → produces artifacts at `{output_folder}/requirements/`.
2. User invokes `tjce-agent-qa` → SKILL.md checks prerequisites.
3. User selects BUILD → produces test cases, unit tests, coverage report, code review.
4. User selects VERIFY → executes tests, classifies defects, emits cycle report with go/no-go.
5. On NO-GO, developer fixes defects, user re-invokes VERIFY → new cycle with regression tracking.

This is a complete and traceable workflow. The headless mode (`--headless build` / `--headless verify`) is defined in both SKILL.md and within each capability, enabling CI/CD integration.

**File path bug (medium severity):** In `verify-capability.md`, the Consolidated Reporting section states:

> Write to `{output_folder}/tests/test-plan.md`.

But the preceding text says "update or create `{output_folder}/reports/test-plan.md`." The section header says "reports" but the write instruction says "tests." This is a direct inconsistency — one of the two paths is wrong, and agents following this prompt will write to an inconsistent location. Given that all other VERIFY outputs go to `{output_folder}/reports/`, the `tests/` path in the write instruction is most likely the bug.

**Fix:** Change the write instruction in `verify-capability.md` to `{output_folder}/reports/test-plan.md`.

---

## Summary Table

| Dimension | Severity | Finding |
|-----------|----------|---------|
| Persona–capability alignment | — | Strong alignment across BUILD and VERIFY |
| Missing celebration step | Low | Persona declares it; capabilities omit it |
| Missing regression testing protocol | Medium | VERIFY tracks fixed defects but no regression scope |
| Missing performance/accessibility scope | Low | Not scoped out explicitly; may cause user confusion |
| Coverage command duplication | Low | Identical bash block in both capabilities |
| VERIFY lacks soft RN traceability warning | Medium | Direct VERIFY invocation loses RN traceability silently |
| Code review as separate capability | Low | Architectural suggestion; current bundling works |
| File path inconsistency in VERIFY | Medium | `tests/test-plan.md` vs. `reports/test-plan.md` |
| End-to-end user journey | — | Coherent; headless mode supported |

---

## Recommended Actions (Priority Order)

1. **(Medium — Bug)** Fix file path in `verify-capability.md` Consolidated Reporting section: change `{output_folder}/tests/test-plan.md` to `{output_folder}/reports/test-plan.md`.

2. **(Medium)** Add advisory in VERIFY's Prerequisites Validation: if `business-rules.md` is absent, warn that RN traceability in cycle report will be incomplete.

3. **(Medium)** Add a "Regression Scope" note in VERIFY: when defects move from "corrigido" to closed, list their linked test cases as regression candidates for the next cycle.

4. **(Low)** Add a one-line scope disclaimer to SKILL.md description: performance, load, and accessibility testing are out of scope for this skill.

5. **(Low — Optional)** Consider splitting code review into a third capability (REVIEW) to remove the clean-session recommendation awkwardness from BUILD.
