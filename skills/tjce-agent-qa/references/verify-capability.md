---
name: verify-capability
menu-code: V
description: Execute tests, document test cycles, classify defects by severity, and generate consolidated reports.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# VERIFY — Execucao e Ciclos de Teste

This capability executes tests, documents results in numbered cycles, classifies defects by TJCE severity, and produces consolidated reports. It can be invoked independently of BUILD — the user may already have test suites in place.

## What Success Looks Like

1. **`{output_folder}/reports/test-cycle-N.md`** — Documented test cycle with pass/fail results, defect classification, and coverage snapshot
2. All defects classified by TJCE severity with evidence
3. Clear go/no-go recommendation based on results

## Prerequisites Validation

Before executing, verify that BUILD artifacts are in place:

- Test cases exist at `{output_folder}/tests/test-cases.md` OR test files exist in the codebase
- If neither exists, inform the user that BUILD should run first, but do not block — the user may have tests from other sources
- **RN traceability advisory:** If `{output_folder}/requirements/business-rules.md` is not available, warn the user that defect-to-RN traceability in the cycle report will be incomplete

## Test Execution

**If Bash tool is available:**

Run the test suites and capture output (backend and frontend are independent — run in parallel when both exist):

```bash
# Run both in parallel
cd {project-root}/backend && python3 -m pytest -v --tb=short --cov --cov-report=term-missing 2>&1 > /tmp/verify-backend.txt &
cd {project-root}/frontend && npx jest --verbose --coverage 2>&1 > /tmp/verify-frontend.txt &
wait
```

Then parse coverage:

```bash
python3 scripts/parse-coverage.py /tmp/verify-backend.txt --threshold 80
python3 scripts/parse-coverage.py /tmp/verify-frontend.txt --threshold 80
```

**If Bash tool is NOT available:**

Provide commands for the user to execute. Analyze pasted output.

**Progression gate:** Do not advance to Defect Classification until you have real test output — either from Bash execution above or pasted by the user. If no output is available, stop and request it. Never fabricate test outcomes, coverage numbers, or defect counts.

## Defect Classification — Esteira TJCE

Every test failure or issue found must be classified:

| Severidade | Criterio | Exemplos |
| ---------- | -------- | -------- |
| **Alta** | Bloqueia completamente funcionalidade ou aplicacao. Sistema inutilizavel. | Crash na inicializacao, perda de dados, falha de autenticacao total, endpoint retorna 500 em fluxo principal |
| **Media** | Bloqueia uso apropriado, mas existe workaround. Funcionalidade comprometida. | Validacao nao funciona mas permite salvar manualmente, busca retorna resultados incompletos, timeout em operacoes longas |
| **Baixa** | Nao compromete objetivo funcional. Problemas de layout, UX, ou cosmeticos. | Texto cortado, alinhamento errado, label incorreto, mensagem de erro generica em vez de especifica |

**Classification rules:**
- Every defect MUST have a severity — no unclassified findings
- When in doubt between two levels, choose the higher severity
- Reference the specific RN violated when applicable
- Include reproduction steps and evidence (error output, screenshot path, stack trace)

## Test Cycle Documentation

Each execution produces a numbered cycle report at `{output_folder}/reports/test-cycle-N.md`:

- **Cycle number** — auto-increment by scanning existing `test-cycle-*.md` files
- **Date and scope** — what was tested and why
- **Environment** — stack versions, OS, relevant config
- **Results summary** — total tests, passed, failed, skipped, coverage %
- **Defect table** — ID, test case, severity, description, RN, status (novo/reaberto/corrigido)
- **Coverage snapshot** — overall and per-module, delta from previous cycle if available
- **Go/No-Go recommendation:**
  - **GO** if: zero Alta, zero Media, coverage ≥80%
  - **GO with caveats** if: zero Alta, Media items have workarounds documented, coverage ≥80%
  - **NO-GO** if: any Alta, or coverage <80%

## Regression Scope

When a cycle contains defects marked as **corrigido**, list their linked test cases as regression candidates for the next cycle. Include a "Regression Candidates" section in the cycle report with: defect ID, original cycle, linked CT IDs, and recommended re-execution scope. This ensures fixes are verified and regressions are caught.

## Consolidated Reporting

After documenting the cycle, update or create `{output_folder}/reports/test-plan.md` with:

- Test strategy overview (stacks, tools, coverage targets)
- Cycle history summary (cycle N: X pass, Y fail, Z% coverage)
- Outstanding defects across cycles
- Traceability matrix: RN → CT → test result status

Write to `{output_folder}/reports/test-plan.md`.

## Headless Mode

If `--headless` or `-H`: execute tests, generate cycle report, classify all defects, and write all artifacts without user interaction. Exit with structured summary: cycle number, pass/fail counts, coverage %, Alta/Media/Baixa counts, go/no-go status.
