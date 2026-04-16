# Enhancement Opportunities Analysis: tjce-gate-check

**Skill:** `skills/tjce-gate-check`
**Date:** 2026-04-16
**Analyst:** DreamBot (creative edge-case & experience innovation)

---

## Skill Understanding

The tjce-gate-check skill is a quality gate that sits between the SPEC (specification) and BUILD (implementation) phases of the TJCE judicial development pipeline. It runs a 3-layer validation -- artifact completeness (40%), cross-reference consistency (30%), and AI-assisted quality assessment (30%) -- producing a weighted score that must reach 90% to pass. The skill operates in both interactive mode (with scope confirmation, complementary decisions, and a mandatory human gate) and headless mode (deterministic exit codes, no prompting, no human gate), making it suitable for both developer workstations and CI pipelines.

---

## User Journeys by Archetype

### 1. First-Timer ("I just finished SPEC, now what?")

**Journey:** User hears "run gate check before BUILD" from a colleague. Types something like "validar gate" or "gate check". Has never seen the output folder structure.

**What goes well:**
- The SKILL.md frontmatter triggers on natural Portuguese phrases ("validar gate", "verificar requisitos").
- Step 1 fail-fast provides clear remediation: "Execute tjce-agent-requirements para gerar user stories."
- The agent-name-in-remediation pattern is excellent -- first-timers get a direct command to fix the problem.

**Edge cases and gaps:**
- **No "where am I" orientation.** If the user has not set up `_bmad-output` or has artifacts in a non-standard location, Step 1 fails with a file-not-found on a path the user does not recognize. There is no pre-flight message like "I expect to find artifacts at `_bmad-output/`. Is that where your SPEC output lives?"
- **No progress breadcrumbs.** The 8-step flow is described but the user sees no numbered progress indicator. After Step 1 passes, silence until Steps 2-3 finish. The user does not know if something hung or is still running.
- **Score display without context.** A first-timer seeing "Score: 87.5 / 90" has no intuition for whether that is fixable in 5 minutes or 2 days. The report says what is wrong but not the effort gradient.
- **Complementary decisions (Step 7) are foreign.** "Tipo de tarefa: nova_funcionalidade | mudanca | correcao_garantia" -- a first-timer building their first feature may not know the TJCE taxonomy. No tooltip or brief explanation is offered.

**Suggestion:** Add a "first-run greeting" paragraph in the On Activation section that briefly explains the 3 layers, expected duration, and what the user needs to have ready. Provide a one-line gloss for each complementary decision option.

---

### 2. Expert ("I know this gate, let me blast through it")

**Journey:** Senior developer who has passed this gate dozens of times. Wants the fastest path to "APROVADO" so they can start coding.

**What goes well:**
- Headless mode with `--headless` is exactly what this user wants for pre-push checks.
- The fail-fast on missing artifacts avoids wasting time on the full pipeline.
- Exit code contract (0/1) integrates cleanly with `&&` chaining.

**Edge cases and gaps:**
- **No `--quiet` / `--summary-only` mode.** The expert does not want to read a narrative report. They want a one-line pass/fail with the score. The skill always generates the full `gate-check-report.md`.
- **No diff-from-last-run.** When re-running after fixing one issue, the expert wants to see "Previously 3 findings, now 1 remaining." The skill has no memory of prior runs.
- **Partial re-run not possible.** If only test cases changed since last run, the expert must re-run all 4 scripts. There is no `--layer quality` to skip completeness/cross-reference checks.
- **No `--fix` auto-remediation.** The expert knows the fix suggestions are correct. A `--fix` flag that auto-invokes the suggested agents would save context-switching time.

**Suggestion:** Add a `--summary` flag that emits a compact one-liner (score, pass/fail, finding count) to stderr before the full report. Consider a `--diff` flag that compares against the most recent verdict.json.

---

### 3. Confused ("My gate check failed but I don't understand why")

**Journey:** User ran the check, got FAIL with score 82.5, sees a list of findings, but cannot connect them to action.

**What goes well:**
- Each finding has a `fix` field with specific agent invocation.
- The report groups by layer, so the user can see which area is weakest.
- The "Inegociaveis" section is explicit: placeholders are never negotiable.

**Edge cases and gaps:**
- **Orphan IDs are confusing.** The user sees "ID orfao: US-999 referenciado mas nao definido" but may not understand what "orphan" means in this context. Is it a typo? A deleted story? The message does not distinguish.
- **Severity vs. blocking is unclear.** An orphan ID is "medium" severity and the SKILL.md says "IDs orfaos = warning -- reporta mas nao bloqueia." But the user reading the findings sees "medium" with no explanation that medium does not block. The mapping from severity to score impact is hidden inside `calculate-gate-score.py` (SEVERITY_DEDUCTIONS).
- **Cross-reference context window of +/-3 lines may miss links.** The `validate-cross-references.py` script looks 3 lines above and below a defined ID for a reference to another ID. If the user structures their document with the US reference in a metadata block 5 lines above the RN definition, the cross-reference check falsely reports a missing link. This is a structural assumption that is never communicated.
- **Empty section detection uses H2/H3 only.** The `_check_empty_sections` regex is `^#{2,3}\s+\S`. If someone uses H4 (`####`) for sub-sections, those are invisible to the checker. An empty H4 section would be missed, while a filled H4 under an otherwise empty H3 would still flag the H3 as empty (since it only has children, not direct body text).

**Suggestion:** Add a "What does this mean?" blurb after each finding category in the report. Make the +/-3 line context window configurable or document it as a known limitation. Consider expanding empty-section detection to H4.

---

### 4. Edge-Case Explorer ("What happens if I...")

**Journey:** Developer testing the boundaries of the system, intentionally or accidentally.

**Discovered edge cases:**

| # | Scenario | Observed Behavior | Risk |
|---|----------|-------------------|------|
| 1 | **File exists but is binary/corrupt** (e.g., truncated UTF-8) | `errors="ignore"` silently drops bad bytes. Script passes but content is garbled. Cross-references may be missed. | Medium -- silent data loss |
| 2 | **Artifact file contains only whitespace** | `st_size > 0` passes the empty-file check, but the file has no real content. Completeness layer gives full marks for a whitespace-only file. | High -- false pass |
| 3 | **ID format US_001 vs US-001** | Regex accepts both `US-001` and `US_001` via `[-_]`, but the normalization always produces `US-{num}` (hyphen). A file using exclusively underscores will have its definitions found but cross-reference matching may break if the context check searches for the hyphenated form. | Medium -- inconsistent matching |
| 4 | **Duplicate IDs** (e.g., RN-001 defined twice) | `defined_ids` is a set, so duplicates are silently collapsed. Two different business rules sharing the same ID is a real specification error that goes completely undetected. | High -- specification defect passes through |
| 5 | **Extremely large artifact files** (10k+ lines) | All scripts read entire files into memory with `.read_text()`. No streaming. For a judicial system generating large case-based specs, this could be a practical concern. | Low -- unlikely but unguarded |
| 6 | **quality-findings.json absent when LLM step (Step 4) is skipped/fails** | `calculate-gate-score.py` lists it in `missing_inputs` but still computes a score. With no quality findings, quality layer gets a perfect 30/30. A missing LLM assessment inflates the score. | Critical -- silent quality bypass |
| 7 | **Concurrent runs writing to same output_folder** | No file locking. Two parallel headless runs on the same folder would race on verdict.json and report.md. | Medium -- CI edge case |
| 8 | **`pendente` false positive** | The placeholder pattern `\bpendente\b` will flag legitimate text like "acao pendente de aprovacao judicial" which may be a valid business rule description, not a placeholder. Portuguese text about pending judicial actions is extremely common in TJCE context. | High -- false positives in the exact domain this tool serves |
| 9 | **Architecture dir with only non-tech md files** | Script checks for `f.name.startswith("tech")`. A file named `technical-overview.md` would fail because it starts with "technical" not "tech". But `tech-design-v2.md` passes. Fragile prefix matching. | Medium -- naming convention dependency |
| 10 | **Test cases file has no CT-xxx IDs** | Cross-reference script would find no CT definitions, so no cross-reference violations. But the quality layer (Step 4) does an LLM assessment of test case quality. If test cases exist but use a different naming convention, the cross-reference layer gives a false pass. | Medium -- convention coupling |

---

### 5. Hostile-Environment ("Everything is broken")

**Journey:** Running on a CI server where Python is a different version, the filesystem is read-only, or the network is down (affecting LLM step).

**What goes well:**
- Scripts are pure Python with no external dependencies (just stdlib).
- `requires-python = ">=3.10"` is documented in PEP 723 headers.
- Exit code contract is well-defined.

**Edge cases and gaps:**
- **No timeout on LLM assessment (Step 4).** Step 4 is the only non-deterministic step. If the LLM hangs or is unavailable, the entire gate check blocks indefinitely. There is no timeout or fallback specified.
- **No graceful degradation when quality-findings.json is missing.** As noted above, a missing LLM result gives a false perfect score. The headless contract should specify behavior: should a missing quality layer be a FAIL, a WARNING, or a configurable default?
- **Read-only filesystem.** Scripts write to `{output_folder}/reports/` but do not check writability first. A read-only mount would produce a Python exception, not a structured error.
- **Permission errors on artifact files.** `read_text()` will raise `PermissionError`. No try/except wraps these calls. The script crashes with a stack trace, not a finding.
- **No structured error output for infrastructure failures.** When a script crashes (bad JSON, permission error, etc.), stderr gets a Python traceback. The SKILL.md does not specify how the LLM orchestrator should distinguish between "script found problems" (exit 1 with valid JSON) and "script itself crashed" (exit 1 with no JSON on stdout). The calculate-gate-score script handles missing files but the orchestration layer has no explicit crash-detection protocol.

**Suggestion:** Define a "degraded mode" contract: if quality-findings.json is absent, the quality layer score should be 0 (not 30). Add filesystem pre-checks. Wrap file reads in try/except for PermissionError. Specify an LLM timeout.

---

### 6. Automator ("I want this in my CI pipeline yesterday")

**Journey:** DevOps engineer integrating gate-check into GitHub Actions or a Jenkins pipeline.

**What goes well:**
- `--headless` is a proper CLI contract with exit codes.
- JSON output to stdout or file.
- No interactive prompts in headless mode.
- Complementary decisions via CLI args.

**Edge cases and gaps:**
- **No machine-readable summary on stdout in headless mode.** The report.md is narrative. The verdict.json is the machine artifact. But if the automator uses `-o` for verdict, the report is only written by the LLM step. In a pure-headless pipeline, who invokes the LLM? The SKILL.md says Step 6 is "LLM" but headless mode is supposed to work without interaction. This is an unresolved architectural question.
- **`--task-type` is optional but semantically required.** In headless mode, missing task-type defaults to `null`. Downstream consumers (tjce-ship, tjce-agent-apf) need this value. A headless pass with null task-type creates a time bomb for the SHIP phase.
- **No `--output-dir` override.** The automator may want findings written to a CI artifacts directory, not `_bmad-output/reports/`. Individual scripts accept `-o` but the orchestrated flow does not expose this.
- **No JSON schema published.** The verdict.json structure is implicit (defined by code). An automator writing a consumer has to read the Python to understand the schema. No JSON Schema file or documentation of the verdict format exists.
- **No idempotency guarantee.** Running the gate check twice on unchanged artifacts produces different timestamps but should produce identical scores. However, Step 4 (LLM quality assessment) is non-deterministic. Two runs may produce different quality-findings.json, leading to different scores. The automator cannot trust that a passing run will pass again.
- **Missing `--continue` / resume support.** Unlike tjce-verify and tjce-ship which have `--continue` with state files, gate-check has no resume capability. If Step 4 (LLM) fails on a transient error, the entire pipeline must restart from Step 1.

**Suggestion:** Publish a JSON Schema for verdict.json. Make `--task-type` required in headless mode (fail-fast if missing). Add `--output-dir` override. Consider caching deterministic layer results so only the LLM layer needs re-running on retry.

---

## Headless Potential Assessment

**Current headless maturity: 7/10**

| Dimension | Score | Notes |
|-----------|-------|-------|
| CLI arg completeness | 8/10 | Covers task-type, manual, data-model, apf-estimate. Missing: output-dir override, layer selection |
| Exit code contract | 9/10 | Clean 0/1. Missing: exit 2 for "partial pass" (unlike tjce-verify/tjce-ship which use exit 2 for human-gate-pending) |
| Output artifact reliability | 6/10 | verdict.json is reliable. report.md depends on LLM. quality-findings.json depends on LLM. Two of three outputs are non-deterministic |
| Error reporting | 5/10 | Missing: structured error output for script crashes, timeout handling, degraded-mode behavior |
| Pipeline integration | 7/10 | Works with basic CI. Missing: schema docs, idempotency, resume, artifact-dir override |

**Key headless gap:** The LLM dependency in Steps 4 and 6 creates a reliability fault line. Steps 1-3 and 5 are fully deterministic. Steps 4 and 6 depend on LLM availability, response quality, and non-determinism. In a CI pipeline, this means the gate check can flake on infrastructure issues unrelated to specification quality.

**Recommendation:** Split the headless contract into two tiers:
- **Tier 1 (deterministic):** Steps 1-3 + score calculation without quality layer. Exit code based on completeness + cross-reference only (70% max).
- **Tier 2 (full):** All steps including LLM. Current behavior.
This lets CI pipelines run Tier 1 as a fast gatekeeper and Tier 2 as a scheduled or optional enrichment.

---

## Key Findings

### High Opportunity

| # | Area | Observation | Suggestion |
|---|------|-------------|------------|
| H1 | Scoring integrity | Missing quality-findings.json gives a false perfect 30/30 on the quality layer. A missing LLM step inflates the score instead of penalizing it. This is the single most dangerous behavior in the skill. | When quality-findings.json is absent, set quality layer score to 0 and add a "quality layer not evaluated" warning to the verdict. Alternatively, treat it as a blocking condition in headless mode. |
| H2 | False positives | The `\bpendente\b` placeholder pattern matches legitimate Portuguese judicial text. In a TJCE system that routinely describes "acoes pendentes", "recursos pendentes", "decisoes pendentes", this will produce persistent false positives that erode trust in the tool. | Replace bare `pendente` with more specific patterns: `\[pendente\]`, `pendente:`, or `status: pendente`. Alternatively, only flag `pendente` when it appears alone on a line or in a known placeholder context (e.g., table cell containing only "pendente"). |
| H3 | Whitespace-only files | `st_size > 0` check passes for files containing only whitespace or newlines. A file with just `\n\n\n` passes completeness. | Add a content-substantiveness check: read the file, strip whitespace, verify length > some minimum (e.g., 50 chars). |
| H4 | Duplicate IDs | Two different business rules or user stories sharing the same ID are silently collapsed by the set-based collection. This is a real specification defect that passes undetected. | Track ID definition counts. Flag any ID defined more than once as a "high" severity finding in the cross-reference layer. |
| H5 | task-type null in headless | Headless mode allows null task-type, but downstream skills (tjce-ship, tjce-agent-apf) depend on this value. A headless pass with null task-type creates a deferred failure. | Make `--task-type` required when `--headless` is set. Exit 1 with a clear message if missing. |

### Medium Opportunity

| # | Area | Observation | Suggestion |
|---|------|-------------|------------|
| M1 | Cross-reference context window | The +/-3 line window for detecting links is a hidden assumption. Documents structured with metadata blocks or long descriptions will produce false negatives. | Make the window configurable (`--context-lines N`, default 5). Document the assumption in the report when cross-reference findings are present. |
| M2 | Architecture file naming | `f.name.startswith("tech")` is fragile. Files named `technical-design.md`, `tech_spec.md`, or `technology-stack.md` may or may not match depending on prefix. | Use a more robust pattern: check for files matching `tech*.md` or a configurable list of acceptable architecture file names. |
| M3 | No progress indication | The 8-step flow provides no intermediate feedback. In interactive mode, the user waits in silence between steps. | Add a step-progress output: "Step 1/8: Completude de Artefatos... PASS", "Step 2/8: Consistencia... running". |
| M4 | No run history / diff | Each run is stateless. The expert cannot see improvement across runs. | Write a `gate-check-history.jsonl` (append-only) with each run's summary. Support `--diff` to compare against last run. |
| M5 | Report only in Portuguese | The report and all findings are in Portuguese. For multi-language teams or external auditors, this limits accessibility. | Respect `{communication_language}` config for finding messages. Consider a `--lang` override for the report. |
| M6 | LLM step lacks timeout/fallback | Step 4 and Step 6 depend on LLM availability with no timeout specification. | Specify a timeout (e.g., 60s per step). On timeout, write a degraded verdict with quality layer scored as 0. |

### Low Opportunity

| # | Area | Observation | Suggestion |
|---|------|-------------|------------|
| L1 | No JSON Schema | verdict.json structure is implicit. Consumers must read Python source. | Publish a `gate-check-verdict.schema.json` alongside the skill. |
| L2 | No `--continue` resume | Unlike sibling skills (tjce-verify, tjce-ship), gate-check has no resume capability. | Add state checkpointing after Step 3 (deterministic steps complete). Allow `--continue` to skip to Step 4. |
| L3 | Empty section H4 blind spot | `_check_empty_sections` only detects H2/H3. H4+ sections are invisible. | Extend regex to `^#{2,6}\s+\S`. |
| L4 | Recommended artifact UX | Missing `threat-model.md` is reported as "low" but the user gets no explanation of why it is recommended or what value it adds. | Add a brief rationale in the finding's `fix` field: "Considere gerar threat-model.md para documentar riscos de seguranca antes do BUILD." |
| L5 | No `--dry-run` | Users cannot preview what the gate check will validate without actually running it. | Add `--dry-run` that lists expected artifacts and checks without executing, useful for first-timers to understand expectations. |

---

## Top Insights

### 1. The Missing LLM Layer Is a Silent Score Inflator (H1)

This is the most consequential finding. The scoring math treats absence of evidence as evidence of absence-of-problems. When `quality-findings.json` does not exist (because the LLM timed out, was unavailable, or the step was skipped), the quality layer receives 0 deductions, which translates to a perfect 30/30. Combined with a clean completeness and cross-reference layer, a project could pass the gate at 100% without any quality assessment ever running. In a judicial system where specification quality directly impacts case-handling software, this is a material risk. The fix is simple: absent layer results should produce the minimum score for that layer, not the maximum.

### 2. The `pendente` False Positive Is a Domain-Specific Trap (H2)

This is an experience design problem disguised as a regex issue. The word "pendente" appears constantly in judicial domain text -- "recurso pendente de julgamento", "processo pendente de distribuicao", "intimacao pendente". Every business rule describing a pending judicial action will trigger a critical finding that blocks the gate. The team will learn to either avoid the word (distorting their specification language) or lose trust in the placeholder checker entirely. Neither outcome is acceptable. The fix must be context-aware: `pendente` is a placeholder when it appears in isolation (a table cell, a standalone line) but is legitimate content when embedded in a sentence.

### 3. Headless Mode Needs a Deterministic Tier (Headless Assessment)

The current headless mode mixes deterministic scripts (Steps 1-3, 5) with non-deterministic LLM steps (Steps 4, 6). This creates a reliability problem for CI integration. An automator cannot guarantee that a passing run will pass again, because the LLM quality assessment may produce different findings on identical input. The sibling skills (tjce-verify, tjce-ship) both have state-based resume via `--continue`, but gate-check does not. Introducing a two-tier headless model -- Tier 1 for deterministic-only (fast, reliable, suitable for pre-commit hooks) and Tier 2 for full assessment (suitable for scheduled or manual CI runs) -- would make the skill significantly more versatile in automation contexts.

---

## Facilitative Patterns Check

| Pattern | Present? | Assessment |
|---------|----------|------------|
| **Scope confirmation before work** | Yes | On Activation confirms scope in interactive mode. Good. |
| **Fail-fast with remediation** | Yes | Step 1 blocks immediately and names the fixing agent. Excellent. |
| **Parallel where independent** | Yes | Steps 2-3 run in parallel. Correctly identified as independent. |
| **Human gate never automated** | Yes | Step 8 is interactive-only. Headless skips it. Correct. |
| **Structured output for consumers** | Partial | verdict.json exists but has no published schema. report.md is narrative but only generated by LLM. |
| **Error vs. finding distinction** | Missing | No protocol distinguishes "script crashed" from "script found problems." Both produce exit 1. The SKILL.md does not specify crash-handling behavior (unlike tjce-verify which explicitly addresses this). |
| **Progress visibility** | Missing | No step-by-step progress output in interactive mode. No intermediate state in headless mode. |
| **Idempotency** | Missing | LLM steps are non-deterministic. No caching of deterministic results. |
| **Resume / checkpoint** | Missing | Unlike tjce-verify and tjce-ship, no state file or `--continue` flag. |
| **Degraded mode** | Missing | No behavior specified for partial infrastructure failures (LLM down, filesystem read-only, permission errors). |

**Overall facilitative score: 6/10** -- The core patterns (fail-fast, parallel, human gate) are solid. The infrastructure resilience patterns (error distinction, degraded mode, resume, idempotency) present in sibling skills are absent here. This is the youngest skill in the pipeline and would benefit from inheriting the error-handling and state-management patterns already established in tjce-verify and tjce-ship.

---

*Analysis complete. Findings ordered by impact. Implementation should prioritize H1 (scoring integrity) and H2 (false positives) as they directly affect the reliability of the gate decision.*
