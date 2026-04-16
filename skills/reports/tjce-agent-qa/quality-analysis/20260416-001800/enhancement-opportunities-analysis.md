# Enhancement Opportunities Analysis — tjce-agent-qa
**Report ID:** 20260416-001800  
**Analyst:** DreamBot — Creative Disruption & User Journey Testing  
**Target skill:** `skills/tjce-agent-qa/`  
**Date:** 2026-04-16  
**Classification:** Advisory — nothing is broken, everything is an opportunity

---

## Executive Summary

`tjce-agent-qa` is a well-structured, principled QA agent with a clear identity and non-negotiable standards. The BUILD and VERIFY capabilities are logically coherent, the parse-coverage tool is properly tested, and the headless declarations give it automation potential. The opportunities below are about closing gaps between what the agent _intends_ and what happens when reality doesn't cooperate — missing artifacts, changed requirements, ambiguous environments, hostile runners, and users who arrive at the wrong door at the wrong time.

---

## 1. Edge Case Stress Test

### 1.1 No Tests Exist Yet

**Scenario:** User invokes VERIFY on a brand-new project. No test files anywhere, no `test-cases.md`.

**Current behavior:** VERIFY's prerequisite check reads "inform the user that BUILD should run first, but do not block — the user may have tests from other sources." This is permissive by design but produces an ambiguous moment: the agent continues into test execution, runs `pytest -v`, and finds zero tests. pytest exits with code 5 (no tests collected). The coverage parser receives an output with no `.py` pattern matches and exits with code 2 ("Could not parse coverage output").

**What the user experiences:** The agent proceeds confidently, hits a wall, and the diagnostic is "ERROR: Could not parse coverage output" — which sounds like a tool failure, not an expected state.

**Opportunity:** Distinguish between *no tests collected* (exit 5 from pytest) and *parse failure*. The prerequisite check should offer a soft decision point: "Nenhum artefato de teste encontrado. Deseja executar BUILD primeiro, ou confirmar que os testes estao em outro local?" This converts a dead-end into a navigation choice.

---

### 1.2 Coverage Tool Not Installed

**Scenario:** `pytest-cov` is not in the environment. `pytest --cov` raises `ModuleNotFoundError: No module named 'pytest_cov'`. Same for `npx jest` when `jest` is not in `node_modules`.

**Current behavior:** BUILD's coverage step runs the command, gets a non-coverage error in stdout, passes it to `parse-coverage.py`, which returns exit code 2. The agent has graceful degradation for "Bash tool NOT available" but no path for "Bash available, tool missing."

**What the user experiences:** The parse failure looks like a script bug, not a missing dependency. The agent may declare a blocking finding based on unrelated error output.

**Opportunity:** Add a pre-flight check before the coverage command: `python3 -m pytest --co -q 2>&1 | head -1` to verify pytest is reachable, and separately check `python3 -m pytest --cov --co -q 2>&1 | grep -i "no module"` to detect missing pytest-cov. Surface the missing dependency with the exact install command. This is a 30-second check that prevents a confusing dead-end.

---

### 1.3 Requirements Changed Between Cycles

**Scenario:** Cycle 1 runs with RN-001 through RN-010. Between cycles, `tjce-agent-requirements` regenerates `business-rules.md` and adds RN-011, modifies RN-007. The user runs VERIFY for Cycle 2.

**Current behavior:** VERIFY re-reads requirement artifacts for cycle documentation but does not diff them against what was used in the previous cycle. Test cases from BUILD (written against the old RN set) are now stale. Traceability matrix in `test-plan.md` will silently have orphaned or missing RN references.

**What the user experiences:** A Cycle 2 report that says "all tests passed" while RN-011 has zero test coverage — a compliance gap that looks like a clean bill of health.

**Opportunity:** At VERIFY activation, if a previous cycle report exists, compare the RN list in `business-rules.md` against the RNs referenced in `test-cases.md`. If any RN appears in requirements but not in test cases, surface it as a traceability gap before execution. This is the agent living its own principle: "se nao esta testado, nao esta pronto."

---

### 1.4 Partial Codebase (Only Backend or Only Frontend)

**Scenario:** The project has only a `frontend/` directory. No `backend/` at all.

**Current behavior:** BUILD scans for both stacks. The backend check runs `cd {project-root}/backend && python3 -m pytest ...` which immediately fails with "directory not found." This is different from "no tests" — it's an execution error that produces no parseable coverage output.

**Opportunity:** The stack detection step (currently described as "scan the codebase") should gate the execution commands. If `backend/` does not exist, skip the backend coverage block entirely and note it in the report. The current spec implies this is the intent but doesn't make it explicit — the LLM may still attempt the command.

---

### 1.5 `parse-coverage.py` Path Resolution

**Current behavior:** Both capabilities call `python3 scripts/parse-coverage.py` as a relative path. The working directory context when running via Bash depends on where the agent is invoked. If the CWD is `{project-root}` and the script lives in the skill directory (not the project), the path is wrong.

**Opportunity:** Document in both capability files that the script path must be resolved as an absolute path relative to the skill directory at runtime. Alternatively, provide the full invocation pattern the agent should use, since it knows `{project-root}` already. This is currently an implicit assumption that breaks silently.

---

## 2. User Archetype Journey Stress Tests

### Archetype 1: First-Timer

**Profile:** Developer who has never used this QA workflow. Comes with code and a vague sense that "I should probably test this."

**Journey:** Activates skill, gets the BUILD/VERIFY menu. Chooses BUILD. Agent immediately checks for requirement artifacts. They don't exist. Agent stops.

**Experience gap:** The stop message says "requirement artifacts are a prerequisite (generated by `tjce-agent-requirements`)". For a first-timer, this raises: what is `tjce-agent-requirements`? How do I get it? Where do I run it? The stop is correct but the exit provides no forward path.

**Opportunity:** When stopping for missing requirements, include: "Para gerar esses artefatos, utilize a skill `tjce-agent-requirements` neste mesmo projeto. Execute `/tjce-agent-requirements` para iniciar." One sentence — but it converts a dead-end into a handoff.

---

### Archetype 2: Expert

**Profile:** Senior QA analyst who knows exactly what they want. Already has test files, wants to run a formal cycle and get a go/no-go with evidence.

**Journey:** Invokes with `--headless verify`. Agent checks prerequisites, detects test files in codebase, runs tests, produces cycle report.

**Delight opportunity:** The expert does not need explanations. In headless mode, the output should be dense and structured — the current spec calls for a "structured summary" which is good. The gap is that the summary format is unspecified. For CI integration, a machine-readable exit code and structured JSON summary would allow the expert to pipe results into a dashboard or Slack notification without parsing prose.

**Opportunity:** Add `--json` flag support to headless mode (mirroring `parse-coverage.py`'s `--json`). Exit 0 for GO, exit 1 for NO-GO — this is already implicit from the go/no-go logic but should be stated explicitly so automation can rely on it.

---

### Archetype 3: Confused User

**Profile:** User who has the requirements and some tests but isn't sure which capability to run. Reads the menu and doesn't understand "BUILD vs VERIFY."

**Experience gap:** The capability names are intentionally technical ("BUILD — Testes e Code Review", "VERIFY — Execucao e Ciclos"). The description in the menu gives codes B and V but doesn't answer "what do I run if I already have some tests and want to check coverage?"

**Opportunity:** The routing presentation could include a decision heuristic in plain language:
- "Precisa gerar casos de teste ou escrever testes unitarios? → BUILD"
- "Ja tem testes escritos e quer executar e documentar um ciclo? → VERIFY"
- "Primeira vez no projeto? → BUILD"

This is a 3-line addition to the ambiguous-intent path that eliminates most confusion cases.

---

### Archetype 4: Edge-Case User

**Profile:** User whose project has 100% test coverage in one file and 0% in another. Total coverage is exactly 79.9%.

**Journey:** Coverage gate blocks. Agent "does not proceed to code review until coverage is resolved or the user explicitly overrides."

**Experience gap:** The "user explicitly overrides" path is mentioned once in BUILD but never defined. What does an override look like? Does the user type "override"? Is there a flag? Is the code review skipped or just flagged?

**Opportunity:** Define the override mechanism explicitly. Suggestion: "Para prosseguir com cobertura abaixo de 80%, responda com `prosseguir mesmo assim`. O relatorio de cobertura sera marcado como BLOQUEADO e o code review tera um aviso no cabecalho." This turns an ambiguous escape hatch into a deliberate, auditable decision.

---

### Archetype 5: Hostile Environment

**Profile:** Running inside a CI pipeline. No interactive terminal. Bash available but restricted (no `cd` into certain paths, `npx` not in PATH, Python 3.8 instead of 3.9+).

**Journey:** `--headless build` invoked. Stack detection runs. `npm` not found for Jest. Python is 3.8, parse-coverage.py uses `dict | None` union syntax (Python 3.10+). Script crashes with `TypeError`.

**Experience gap (critical):** `parse-coverage.py` uses `dict | None` return type annotations which require Python 3.10+. The script header specifies `requires-python = ">=3.9"` but the syntax fails on 3.9 as well — `dict | None` in function signatures is only valid from Python 3.10. If run on Python 3.9, it will fail at import time with a `TypeError`.

**Opportunity (P1 bug-adjacent):** Change `dict | None` to `Optional[dict]` from `typing` (or use `from __future__ import annotations`) in `parse-coverage.py`. Update the requires-python to `>=3.10` if the union syntax is intentional. This is a real failure mode in environments like TJCE's judicial servers which may run older Python distributions.

**Additional opportunity:** In headless mode, if any tool invocation fails (non-zero exit, missing command), write a machine-readable `errors.json` to the output folder alongside the report. This gives CI pipelines a structured failure artifact beyond the exit code.

---

### Archetype 6: Automator

**Profile:** DevOps engineer wiring the QA skill into a nightly pipeline. Wants deterministic, repeatable, zero-interaction runs.

**Journey:** Calls `--headless verify` on a schedule. Expects cycle numbers to auto-increment, reports to be written to predictable paths, exit code to reflect go/no-go.

**Headless completeness assessment:**

The headless declarations exist in both capabilities. Assessing completeness:

| Feature | Declared | Fully Specified | Gap |
|---------|----------|-----------------|-----|
| Non-interactive execution | Yes | Yes | — |
| Route directly to capability | Yes | Yes | — |
| Exit with structured summary | Yes | Prose only | No machine-readable format |
| Override coverage block | Yes (BUILD) | No | Override mechanism undefined |
| Cycle number auto-increment | Yes | Yes (scan existing files) | No conflict resolution if two parallel runs write simultaneously |
| Config loading (`_bmad/config.yaml`) | Yes | Yes | No spec for missing config in headless |
| Error artifacts | No | No | No structured error output |
| Exit codes | Implicit (go/no-go) | No | Not stated explicitly |

**Opportunity:** Add a "Headless Contract" section to SKILL.md that formally specifies: exit codes (0=GO, 1=NO-GO, 2=error/missing prerequisites), output file locations, and the behavior when config files are absent. This makes the automation contract testable and removes ambiguity for CI integration.

---

## 3. Assumption Audit

### 3.1 Linear Progression Assumption

The skill assumes BUILD before VERIFY. VERIFY's prerequisite check softens this, but the traceability matrix in `test-plan.md` is built assuming `test-cases.md` exists as the source of truth. If the user has test files but no `test-cases.md`, the traceability matrix will be empty — not wrong, but misleading.

**Opportunity:** When building the traceability matrix without `test-cases.md`, derive it by scanning test function names/docstrings for RN references. This makes the matrix useful even in "tests exist but BUILD was skipped" scenarios.

---

### 3.2 Single-Instance Assumption

The skill assumes one agent session at a time. The cycle counter increments by scanning `test-cycle-*.md` files — this is a file-based counter with no locking. In automated pipelines with parallel runs, two agents could both read "no cycles exist" and both write `test-cycle-1.md`.

**Opportunity:** Use a timestamp-based cycle identifier as a fallback: if `test-cycle-1.md` already exists when the agent tries to write it, increment until a free slot is found. This is a one-line behavioral addition.

---

### 3.3 Input Quality Assumption

BUILD's code review step reads "Review the application source code (`{project-root}/backend/`, `{project-root}/frontend/src/`)". This assumes standard directory names. A TJCE project may use `app/`, `src/`, `api/`, or a monorepo structure.

**Opportunity:** The stack detection step already scans for `backend/` or `frontend/`. Reuse those resolved paths in the code review step instead of hardcoding directory names. If neither standard path exists, ask the user to specify the source root before proceeding.

---

### 3.4 Context Window Assumption

BUILD step 4 (Code Review) already acknowledges context window pressure with the "recommend separate session" note — this is a well-designed facilitative gate. The opportunity: make the recommendation smarter. If the session has generated more than ~50 test cases or written more than 5 test files, trigger the recommendation automatically rather than always. The current instruction triggers it whenever tests were generated in the same session, which is every normal BUILD session.

**Opportunity:** Reframe as a capability: "Estou preparando o code review. Esta sessao ja gerou [N] casos de teste e [M] arquivos. Para um code review mais preciso, recomendo uma sessao separada (responda 'separar') ou posso continuar aqui (responda 'continuar')." Give the user data to make the decision rather than always recommending separation.

---

## 4. Delight Opportunities

### 4.1 Progress Awareness in Headless Mode

In a long headless run (test generation + unit tests + coverage + code review), the user has no visibility. The spec says "execute all four steps sequentially" but doesn't specify any progress signaling.

**Opportunity:** Emit structured progress markers to stdout even in headless mode:
```
[BUILD 1/4] Gerando casos de teste... (RN-001 a RN-012)
[BUILD 2/4] Gerando testes unitarios... (backend: pytest)
[BUILD 3/4] Verificando cobertura...
[BUILD 4/4] Executando code review...
[BUILD DONE] 4 etapas concluidas. Cobertura: 87%. Findings: 3 Alta, 1 Media, 2 Baixa.
```
This makes headless runs debuggable and gives CI logs meaningful signal.

---

### 4.2 Delta Reporting Between Cycles

VERIFY already mentions "delta from previous cycle if available" for coverage. This is a delight feature worth expanding: between Cycle N-1 and Cycle N, show not just coverage delta but:
- New defects introduced
- Defects resolved
- RNs that went from uncovered to covered

A "Cycle Delta" section at the top of each cycle report gives the reader the answer to "what changed?" without reading two full reports.

---

### 4.3 Proactive Insight: Orphaned Tests

When generating the traceability matrix, the agent checks RN → CT coverage. The inverse check — CT → RN — would surface tests that have no RN link. These "orphaned tests" test something real but don't prove compliance. Flagging them as "testes sem rastreabilidade: existem mas nao provam nada sobre a spec" (the agent's own language from SKILL.md) gives the team an actionable cleanup list.

---

### 4.4 Smart Default for Missing Config

When `_bmad/config.yaml` is absent, the agent uses hardcoded defaults. An opportunity to delight: on first activation without config, ask one question: "Qual e o seu nome? Vou usar para personalizar os relatorios." Store in session state. This creates a personal touch with zero friction and makes the reports feel authored rather than generated.

---

## 5. Facilitative Patterns — Current State and Gaps

| Pattern | Present? | Quality | Enhancement |
|---------|----------|---------|-------------|
| Soft gate before code review | Yes | Good — offers choice | Make it data-driven (see 4.4) |
| Intent-before-ingestion at routing | Partial | Covers ambiguous intent but not sub-capability ambiguity | Add decision heuristic for confused users |
| Capture-don't-interrupt in Bash-unavailable | Yes | Good — asks user to paste output | Should also work for partial output (user pastes truncated log) |
| Graceful degradation for Bash | Yes | Full alternative path | No graceful degradation for broken Bash (tool present but commands fail) |
| Override escape hatch at coverage block | Mentioned | Mechanism undefined | Formalize override phrase and its audit trail |
| Prerequisite check at activation | Yes | Hard stop with explanation | Add forward pointer to `tjce-agent-requirements` |
| Progress visibility | No | Missing | Add progress markers especially for headless |

---

## 6. Headless Completeness Assessment

**Declared support:** Both BUILD and VERIFY declare `--headless` / `-H`.

**Current completeness: ~65%**

What works:
- Routing directly to capability without menu
- Executing all steps without prompting
- Writing artifacts to standard output paths
- Continuing past coverage block (BUILD headless overrides the block)

What is missing or underspecified:
- **Exit codes:** Never formally defined. GO/NO-GO implies 0/1 but this is not stated.
- **Structured output:** Only prose summary specified. No JSON mode for machine consumption.
- **Error handling:** No spec for what happens when a prerequisite file is missing mid-run.
- **Config absence:** Undefined behavior when `_bmad/config.yaml` doesn't exist.
- **Override audit trail:** The BUILD headless override of the coverage block produces no explicit marker in the artifact that the coverage gate was bypassed.
- **Parallel safety:** Cycle number collisions in concurrent runs.
- **Partial Bash failure:** No fallback if `cd {project-root}/backend` fails (dir not found).

**To reach 90% completeness**, add a "Headless Contract" section to SKILL.md (see Archetype 6 above) and handle the Bash partial-failure path in both capabilities.

---

## 7. Priority Summary

| # | Opportunity | Impact | Effort | Archetype |
|---|-------------|--------|--------|-----------|
| 1 | Fix `dict \| None` Python 3.9 incompatibility in parse-coverage.py | High | Low | Hostile-environment |
| 2 | Define explicit headless exit codes and contract | High | Low | Automator |
| 3 | Add forward pointer to `tjce-agent-requirements` in prerequisite stop | High | Low | First-timer |
| 4 | Define coverage override mechanism and its audit trail | Medium | Low | Edge-case |
| 5 | Distinguish "no tests collected" from "parse failure" (exit 5 handling) | Medium | Medium | First-timer, Edge-case |
| 6 | Pre-flight check for missing coverage tools (pytest-cov, jest) | Medium | Low | Hostile-environment |
| 7 | Requirements drift detection between cycles | Medium | Medium | Edge-case |
| 8 | Decision heuristic text in capability routing | Low | Low | Confused |
| 9 | Delta reporting in cycle reports | Low | Medium | Expert |
| 10 | Orphaned test detection in traceability matrix | Low | Medium | Expert, Automator |
| 11 | Progress markers in headless mode | Low | Low | Automator |
| 12 | JSON output flag for headless structured summary | Low | Low | Automator |

---

## Appendix: Script-Level Finding (Requires Code Change)

**File:** `skills/tjce-agent-qa/scripts/parse-coverage.py`  
**Lines:** 32, 80  
**Issue:** `dict | None` union syntax requires Python 3.10+. The script's `requires-python = ">=3.9"` is incorrect. On Python 3.9, the script crashes at import with `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`.

**Fix options:**
1. Add `from __future__ import annotations` as the first import (enables PEP 563 deferred evaluation, resolves at 3.7+)
2. Replace `dict | None` with `Optional[dict]` from `typing`
3. Update `requires-python = ">=3.10"` to truthfully reflect the requirement

Option 1 is the lowest-friction fix. Option 3 is the most honest.

This is the only finding that requires a code change rather than prompt/documentation changes.
