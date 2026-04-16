---
name: build-capability
menu-code: B
description: Generate test cases from requirements, produce unit tests, verify coverage, and perform code review.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# BUILD — Testes e Code Review

This capability covers four deliverables: test cases document, unit test code, coverage verification, and code review. All test cases must trace back to Business Rules (RN) from the requirement artifacts.

## What Success Looks Like

1. **`{output_folder}/tests/test-cases.md`** — Complete test case catalog derived from requirements, every case linked to at least one RN
2. **Unit test files** written in the codebase — pytest (backend) and/or Jest (frontend)
3. **`{output_folder}/reports/coverage-report.md`** — Coverage ≥80% verified with real tool output
4. **`{output_folder}/reports/code-review.md`** — Code review findings with severity, location, and evidence

## 1. Test Cases Generation

Read the requirement artifacts:
- `{output_folder}/requirements/user-stories.md`
- `{output_folder}/requirements/business-rules.md`
- `{output_folder}/requirements/messages.md`

Derive test cases from Business Rules. Each test case must include:

| Campo | Descricao |
| ----- | --------- |
| ID | CT-NNN (sequencial) |
| Titulo | Descricao curta do cenario |
| RN | Regra(s) de Negocio vinculada(s) |
| Pre-condicao | Estado necessario antes da execucao |
| Passos | Acoes para executar o teste |
| Resultado Esperado | O que o sistema deve fazer |
| Tipo | unitario / integracao / e2e |

**Traceability constraint:** Every RN in `business-rules.md` must have at least one test case. After generating, run the traceability validator:

```bash
python3 scripts/validate-traceability.py {output_folder}/requirements/business-rules.md {output_folder}/tests/test-cases.md
```

If any RN is uncovered, add test cases before proceeding.

Write test cases to `{output_folder}/tests/test-cases.md`.

## 2. Unit Test Code Generation

Detect the project stack by scanning the codebase:
- **If `{project-root}/backend/` or `pytest` in dependencies:** Generate pytest tests
- **If `{project-root}/frontend/` or `jest` in dependencies:** Generate Jest tests
- **If both:** Generate for both stacks

Generate test files that implement the test cases from step 1. Place them following the project's existing test directory conventions (e.g., `backend/tests/`, `frontend/src/__tests__/`). If no convention exists, use `tests/` at the stack root.

Each test function should reference its test case ID in a comment or docstring for traceability.

## 3. Coverage Verification

**If Bash tool is available:**

Run coverage tools (backend and frontend are independent — run in parallel when both exist):

```bash
# Run both in parallel
cd {project-root}/backend && python3 -m pytest --cov --cov-report=term-missing 2>&1 > /tmp/coverage-backend.txt &
cd {project-root}/frontend && npx jest --coverage 2>&1 > /tmp/coverage-frontend.txt &
wait
```

Then parse results (also parallelizable):

```bash
python3 scripts/parse-coverage.py /tmp/coverage-backend.txt --threshold 80
python3 scripts/parse-coverage.py /tmp/coverage-frontend.txt --threshold 80
```

**If Bash tool is NOT available:**

Provide the exact commands for the user to run, and ask them to paste the output. Analyze the pasted output the same way.

**Coverage gate:** If total coverage < 80%, declare a blocking finding. Identify the specific modules/functions below threshold, suggest the tests that would close the gap, and do not proceed to code review until coverage is resolved or the user explicitly overrides.

**Override mechanism:** To proceed with coverage below 80%, the user must respond with "prosseguir mesmo assim" (or equivalent explicit override). When overridden, mark the coverage-report.md header with `**BLOQUEIO DE COBERTURA IGNORADO — decisao do usuario em {data}**`. In headless mode, always continue but mark the report.

Write coverage results to `{output_folder}/reports/coverage-report.md`.

## 4. Code Review

**Recommendation:** Code review produces better results in a clean context window. If this session has already generated tests, inform the user: "Recomendo realizar o code review em uma sessao separada para contexto limpo. Deseja continuar aqui mesmo assim?" If the user proceeds, add a disclaimer to the review report header.

Review the application source code (`{project-root}/backend/`, `{project-root}/frontend/src/`) against the approved spec. Focus areas:

- **Bugs and logic errors** — code behavior vs. spec intent
- **Security vulnerabilities** — injection, auth bypass, data exposure (OWASP Top 10)
- **Architecture violations** — coupling, layer violations, dependency direction
- **Dead code** — unreachable branches, unused imports, commented-out blocks
- **Unnecessary complexity** — functions doing too much, deep nesting, unclear naming

Each finding must include: file path, line number(s), severity (Alta/Media/Baixa per TJCE classification), description, and evidence (the problematic code).

Write review to `{output_folder}/reports/code-review.md`.

## Headless Mode

If `--headless` or `-H`: execute all four steps sequentially without user interaction. Use sensible defaults for stack detection. If coverage < 80%, write the report with the blocking finding but continue to code review (both reports are valuable even if coverage blocks deployment). Exit with a summary of pass/fail status.
