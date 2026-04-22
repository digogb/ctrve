---
name: functional-and-security
description: Steps 3-4 — Execute functional test cases via tjce-agent-qa and run deterministic security scans.
---

# Stages 3-4 — Verificacao Funcional e de Seguranca

**Stages 3 and 4 are independent — execute them in parallel** when subagents or parallel tool calls are available. If not, execute sequentially.

## Stage 3 — Verificacao Funcional

Execute the test cases documented in `{output_folder}/tests/test-cases.md` through a formal test cycle.

**Delegation to tjce-agent-qa:** Invoke the VERIFY capability — it handles test case execution, TJCE severity classification (Alta/Media/Baixa), and numbered cycle report generation. Do not replicate this logic.

**Orchestration:**

1. Determine the next cycle number by scanning existing `{output_folder}/reports/test-cycle-*.md` files
2. Invoke `tjce-agent-qa verify` to execute the test cycle
3. Validate the generated `{output_folder}/reports/test-cycle-N.md` contains: execution results, defect classifications, and Go/No-Go recommendation

**No blocking gate here** — functional findings feed into consolidation.

## Stage 4 — Verificacao de Seguranca

Deterministic security scans — script-based, not agent-based.

**Execute both scans in parallel and format the report:**

```bash
python3 scripts/scan-secrets.py {project-root}/backend {project-root}/frontend -o /tmp/secrets-result.json &
python3 scripts/validate-security.py {project-root}/backend {project-root}/frontend -o /tmp/security-result.json &
wait
python3 scripts/format-security-report.py /tmp/secrets-result.json /tmp/security-result.json -o {output_folder}/reports/security-report.md
```

Validate that both scripts produce valid JSON before passing to the formatter. If either script produces no JSON output, treat as infrastructure error per the Error Recovery section in SKILL.md.

**Security gate:**
- Any **critical** finding: BLOCK. Report vulnerabilities and recommend returning to BUILD. Exit 1 in headless.
- High/medium/low findings: document and proceed — they feed into consolidation.

**Progression:** If not blocked, load `references/consolidation-and-gate.md`.
