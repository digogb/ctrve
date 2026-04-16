---
name: functional-and-security
description: Steps 3-4 — Execute functional test cases via tjce-agent-qa and run deterministic security scans.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by SKILL.md at activation time.

# Stages 3-4 — Verificacao Funcional e de Seguranca

## Stage 3 — Camada 2: Verificacao Funcional

Execute the test cases documented in `{output_folder}/tests/test-cases.md` through a formal test cycle.

**Delegation to tjce-agent-qa:** Invoke the VERIFY capability — it handles test case execution, TJCE severity classification (Alta/Media/Baixa), and numbered cycle report generation. Do not replicate this logic.

**Orchestration:**

1. Determine the next cycle number by scanning existing `{output_folder}/reports/test-cycle-*.md` files
2. Invoke `tjce-agent-qa verify` to execute the test cycle
3. Review the generated `{output_folder}/reports/test-cycle-N.md`

**Verify the cycle report contains:**
- Execution results for all test cases from `test-cases.md`
- Defects classified by TJCE severity with evidence
- Go/No-Go recommendation

**No blocking gate here** — functional findings feed into consolidation. Alta defects affect the final Go/No-Go but do not halt the pipeline at this stage. Proceed to Stage 4.

## Stage 4 — Camada 3: Verificacao de Seguranca

Deterministic security scans — script-based, not agent-based.

**Execute both scans** (independent, can run in parallel):

```bash
python3 scripts/scan-secrets.py {project-root}/backend {project-root}/frontend
python3 scripts/validate-security.py {project-root}/backend {project-root}/frontend
```

**scan-secrets.py** — detects hardcoded secrets, tokens, API keys, and credentials. Ignores test fixtures, `.env.example`, and documentation.

**validate-security.py** — checks for OWASP basics: raw SQL (non-parameterized), missing input validation, CORS misconfiguration, insecure auth patterns.

**Output:** Write `{output_folder}/reports/security-report.md` combining findings from both scans:
- Findings organized by severity (critical/high/medium/low)
- File path and line number for each finding
- Category (secrets, injection, CORS, auth, input validation)

**Security gate:**
- Any **critical** finding: BLOCK. Report vulnerabilities and recommend returning to BUILD. Exit 1 in headless.
- High/medium/low findings: document and proceed — they feed into consolidation.

**Progression:** If not blocked, load `references/consolidation-and-gate.md`.
