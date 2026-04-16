---
name: pre-check-and-automated
description: Steps 1-2 — Validate BUILD artifacts exist and execute automated verification layer via tjce-agent-qa.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and `{coverage_threshold}` are resolved by SKILL.md at activation time.

# Stages 1-2 — Pre-Check e Verificacao Automatizada

## Stage 1 — Pre-Check de Artefatos BUILD

Validate that the BUILD phase produced all required artifacts before any verification begins.

**Run the pre-check script:**

```bash
python3 scripts/check-build-artifacts.py {output_folder}
```

**Required artifacts:**
- `{output_folder}/tests/test-cases.md`
- `{output_folder}/reports/code-review.md`
- `{output_folder}/reports/coverage-report.md`

**Optional** (checked but not blocking):
- `{output_folder}/architecture/data-model.md`

**If any required artifact is missing:** BLOCK. Report exactly which artifacts are missing and inform the user to run BUILD (`tjce-agent-qa build`) first. Exit 1 in headless.

**If all present:** Report status and proceed to Stage 2.

## Stage 2 — Camada 1: Verificacao Automatizada

Invoke `tjce-agent-qa` with capability VERIFY in headless mode to execute the automated test suite.

**What tjce-agent-qa VERIFY handles** (delegate, do not duplicate):
- Test suite execution (pytest backend, jest frontend)
- Coverage metrics capture
- Test failure classification by TJCE severity

**Orchestration:**

1. Invoke `tjce-agent-qa --headless verify` and capture results
2. Read the generated test cycle report from `{output_folder}/reports/`
3. Parse coverage percentage from the cycle report

**Coverage gate:**
- Coverage >= `{coverage_threshold}`%: PASS — proceed
- Coverage < `{coverage_threshold}`%: BLOCK — report which modules are below threshold and recommend returning to BUILD. Exit 1 in headless.

**Output:** Write `{output_folder}/reports/verify-layer1-automated.md` with:
- Timestamp and execution environment
- Test execution summary (total, passed, failed, skipped)
- Coverage percentage and per-module breakdown
- Pass/Block status with reasoning
- If blocked: specific gaps and recommended actions

**Progression:** If PASS, load `references/functional-and-security.md`.
