# Script Opportunities Analysis — tjce-ship

**Skill:** `skills/tjce-ship/`
**Date:** 2026-04-16T19:12:20
**Analyzer:** ScriptHunter

---

## 1. Existing Scripts Inventory

| Script | Purpose | Quality | Test Coverage |
| ------ | ------- | ------- | ------------- |
| `scripts/check-verify-status.py` | Check that tjce-verify completed with APROVADO status | Excellent — reads verify-verdict.json and verify-summary.md, JSON output, proper exit codes | Yes (`test_check-verify-status.py`) |
| `scripts/detect-task-type.py` | Detect task type and manual flag from CLI args, config, or requirements | Excellent — cascading inference (CLI > config.json > YAML > requirements.md), JSON output | Yes (`test_detect-task-type.py`) |
| `scripts/check-deliverables.py` | Validate all expected release artifacts exist based on task type and flags | Excellent — conditional artifact matrix, markdown/JSON dual output, checklist generation | Yes (`test_check-deliverables.py`) |
| `scripts/generate-ship-summary.py` | Aggregate all release artifacts into final ship summary and verdict | Excellent — reads ship-state.json, produces both JSON verdict and markdown report | Yes (`test_generate-ship-summary.py`) |

**Assessment:** The existing script suite is exceptionally well-designed for an orchestrator skill. All four scripts follow a consistent contract: JSON output, exit code discipline (0=pass, 1=fail), `--output`/`--verbose`/`--format` flags, and unit tests. The skill already delegates all major pre-processing (Steps 1, 7) and post-processing (Step 9) to scripts, with the LLM acting purely as an orchestrator for agent delegation and human gate management. This analysis found fewer remaining opportunities compared to leaf-agent skills, which is expected for an orchestrator.

---

## 2. Findings

### Finding 1 — PML Structural Validation (Step 3)

- **Severity:** High
- **File:** `references/pre-check-and-release.md`, lines 59-62
- **Current work in prompt:** "Validate the generated `{output_folder}/release/PML.md`: File exists and is non-empty; No sections contain only placeholders, 'TODO', 'a definir', or are empty"
- **Determinism test:** This is pure structural validation. Checking file existence, non-emptiness, and scanning for forbidden placeholder patterns ("TODO", "a definir", empty sections between markdown headers) are all regex-based operations. Identical PML content always produces the same pass/fail result. The "Inegociaveis" section in SKILL.md elevates this to a hard blocker ("PML nunca com secoes vazias ou placeholder"), making correctness critical — and scripts are more reliable than LLM judgment for pattern matching.
- **Script alternative:** A `validate-pml.py` that: (a) checks file existence and non-zero size, (b) extracts all markdown H2/H3 sections, (c) checks each section body for forbidden patterns (TODO, a definir, TBD, placeholder, empty body), (d) returns JSON with section names, their status (valid/empty/placeholder), and overall pass/fail. The LLM then only needs to decide whether to block or re-invoke the agent.
- **Estimated LLM tax:** ~300-500 tokens per invocation (reading the PML file, scanning each section, pattern matching for placeholders, structuring the validation result)
- **Note:** This is the highest-value opportunity because it guards a non-negotiable rule. The LLM might miss a subtle placeholder in a long PML document. A script with explicit regex patterns is both faster and more reliable.

### Finding 2 — Release Artifact Existence Validation (Step 2)

- **Severity:** Medium
- **File:** `references/pre-check-and-release.md`, lines 47-49
- **Current work in prompt:** "Validate that the agent produced all three required artifacts: `CHANGELOG.md`, `deploy-checklist.md`, `rollback-plan.md`. If any artifact is missing, treat as agent failure — do not proceed."
- **Determinism test:** Checking three file paths for existence is trivially deterministic. Identical filesystem state always produces the same result. This is a simpler version of what `check-deliverables.py` (Step 7) already does — but `check-deliverables.py` runs after Steps 5-6 and checks the full set. Step 2 needs an intermediate check of just the release agent outputs.
- **Script alternative:** Reuse `check-deliverables.py` with a `--stage 2` flag that limits the check to just the three release artifacts. Alternatively, a small `validate-release-artifacts.py` that checks the three files and returns JSON. However, this may be over-engineering since `check-deliverables.py` already handles the full superset at Step 7.
- **Estimated LLM tax:** ~100-200 tokens per invocation (three file existence checks and error reporting)
- **Note:** Medium severity because the token cost is low and the operation is simple. However, there is a design consistency argument: if Step 7 uses a script for artifact validation, Step 2 should too. Consider adding a `--partial` or `--stage` flag to `check-deliverables.py` rather than creating a new script.

### Finding 3 — Ship State Checkpoint Management (All Steps)

- **Severity:** Medium
- **File:** `SKILL.md`, line 47; referenced across all three reference files
- **Current work in prompt:** "After each step completes, update `{output_folder}/release/ship-state.json` with current step, timestamp, task type, and flags. On re-invocation, detect existing state and offer to resume."
- **Determinism test:** Writing a JSON file with stage number, ISO timestamp, task type, flags, and status is entirely deterministic. Reading an existing state file and determining which step to resume from is also deterministic (compare stage number to pipeline sequence). The LLM is performing serialization/deserialization of structured state on every step transition — this is called 9+ times per full pipeline run.
- **Script alternative:** A `manage-ship-state.py` with subcommands: (a) `init` — create initial state, (b) `update --stage N --status S` — advance state, (c) `read` — output current state as JSON, (d) `resume-from` — return the next step number to execute. The LLM invokes the script at each checkpoint instead of constructing JSON manually. This eliminates the risk of malformed state files and inconsistent timestamp formats.
- **Estimated LLM tax:** ~150-250 tokens per checkpoint x 9 checkpoints = ~1,350-2,250 tokens per full pipeline run (JSON construction, field names, timestamp formatting, file writing logic)
- **Note:** This is the highest aggregate token cost because it repeats at every step. The per-invocation cost is modest, but the cumulative impact across a full 9-step pipeline run is significant. A state management script would also make the resume logic more robust — the LLM would not need to parse the state file and determine the correct resume point.

### Finding 4 — Agent Availability Pre-Flight Check (Step 1)

- **Severity:** Low
- **File:** `references/pre-check-and-release.md`, lines 29-35
- **Current work in prompt:** "Verify that the required agents are accessible: tjce-agent-release (always needed), tjce-agent-apf (needed unless correcao_garantia), tjce-agent-docs (needed only if manual_necessario). If any required agent is unavailable, report and halt."
- **Determinism test:** The conditional logic (which agents to check based on task_type and manual_necessario) is fully deterministic. The actual availability check mechanism depends on the agent framework — if it is a filesystem check (does the skill directory exist?), it is deterministic. If it requires invoking the agent, it is not scriptable. The conditional filtering is deterministic regardless.
- **Script alternative:** A `check-agent-availability.py --task-type T [--manual-required]` that: (a) determines which agents are needed based on flags, (b) checks each agent's skill directory existence (e.g., `skills/tjce-agent-release/SKILL.md` exists), (c) returns JSON with required agents and their availability. The script handles the conditional logic; the LLM only needs to react to the result.
- **Estimated LLM tax:** ~150-200 tokens per invocation (conditional logic evaluation, three directory checks, error formatting)
- **Note:** Low severity because this runs once per pipeline invocation, the conditional logic is simple, and the actual "availability check" mechanism may not be purely filesystem-based. However, scripting this would eliminate the risk of the LLM forgetting to check an agent (e.g., skipping the manual agent check when manual_necessario is true).

### Finding 5 — Headless Exit Code and Verdict JSON Assembly (Steps 4, 8)

- **Severity:** Low
- **File:** `references/validation-and-artifacts.md`, lines 28-29; `references/deployment-and-closure.md`, lines 28-29
- **Current work in prompt:** "Write ship-state.json with stage=4 and status=awaiting_pml_validation. Exit with code 2." and "Write ship-state.json with stage=8 and status=awaiting_deployment. Exit with code 2."
- **Determinism test:** These are fixed JSON writes with predetermined field values. The content is fully known at prompt-authoring time. The LLM is constructing a JSON literal from a template.
- **Script alternative:** This is subsumed by Finding 3 (state management script). A `manage-ship-state.py update --stage 4 --status awaiting_pml_validation` eliminates the need for the LLM to construct the JSON.
- **Estimated LLM tax:** ~100-150 tokens per gate (JSON construction) x 2 gates = ~200-300 tokens per pipeline run
- **Note:** Low severity because this is subsumed by the state management script in Finding 3. Listed separately for completeness because it also touches the headless exit code contract.

---

## 3. Aggregate Impact

| # | Finding | Severity | Tokens/invocation | Determinism % |
|---|---------|----------|-------------------|---------------|
| 1 | PML structural validation | **High** | 300-500 | 100% |
| 2 | Release artifact existence check | Medium | 100-200 | 100% |
| 3 | Ship state checkpoint management | Medium | 1,350-2,250 (cumulative) | 100% |
| 4 | Agent availability pre-flight | Low | 150-200 | ~80% |
| 5 | Headless exit/verdict assembly | Low | 200-300 (cumulative) | 100% |

**Total estimated LLM tax on deterministic work:** 2,100-3,450 tokens per full pipeline run.

**Context:** The existing 4 scripts already handle the heaviest deterministic operations (verify status check, task type detection, full deliverables check, and ship summary generation). The remaining opportunities are mostly infrastructure plumbing (state management, intermediate validation) rather than data-intensive transformations. The skill is in notably good shape compared to leaf-agent skills.

**Priority ranking by ROI (savings vs. implementation effort):**

1. **Finding 1 — PML structural validation** (High / moderate implementation). Guards a non-negotiable rule. Eliminates ~300-500 tokens of pattern matching per invocation and increases correctness. A ~60-line script with section extraction and placeholder pattern matching.

2. **Finding 3 — Ship state management** (Medium / moderate implementation). Highest aggregate token savings (~1,350-2,250 per full run) because it repeats 9+ times. Also eliminates state serialization bugs. A ~80-line script with init/update/read/resume-from subcommands. Subsumes Finding 5.

3. **Finding 2 — Release artifact intermediate check** (Medium / trivial implementation). Extend `check-deliverables.py` with a `--stage 2` flag to validate only the three release artifacts. Near-zero effort since the script already has the artifact validation logic.

4. **Finding 4 — Agent availability check** (Low / low effort). Useful for robustness but low token savings. ~30-line script. Implementation depends on agent framework conventions.

---

## 4. What Is Correctly Kept as Prompt

The following operations in the prompts **should remain as LLM work**:

- **Agent delegation and orchestration** (invoking tjce-agent-release, tjce-agent-apf, tjce-agent-docs with appropriate context and parameters — requires understanding project context)
- **Human gate interaction** (presenting PML to DevOps, capturing APROVADO/AJUSTAR feedback, understanding specific adjustment requests, presenting checklist to PO)
- **AJUSTAR feedback loop** (interpreting what the reviewer wants changed, re-invoking the agent with feedback context — requires natural language understanding)
- **RDM capture and interpretation** (understanding deployment confirmation, parsing RDM number and date from conversational input)
- **Scope confirmation in interactive mode** (identifying the feature being shipped, confirming task type with the user — requires conversational context)
- **Error communication** (explaining WHY something is blocked, what step failed, and what the user should do — requires context-sensitive natural language)
- **Resume decision** (when ship-state.json exists, offering to resume and interpreting the user's choice — the detection is scriptable via Finding 3, but the user interaction is not)

---

## 5. Recommendations

### Immediate (Finding 1 — eliminate ~300-500 tokens, increase correctness)

Create one script:

1. **`scripts/validate-pml.py`** — Reads `{output_folder}/release/PML.md`, extracts all H2/H3 sections, validates each section body against forbidden patterns (TODO, a definir, TBD, placeholder, empty body between headers). Returns JSON with per-section results and overall pass/fail. Input: output_folder path. Output: JSON with `status`, `sections` array (name, line, content_length, issues), and `findings` array.

### Short-term (Findings 2, 3 — eliminate ~1,450-2,450 tokens)

2. **`scripts/manage-ship-state.py`** — State checkpoint manager with subcommands:
   - `init --task-type T [--manual-required]` — Create initial ship-state.json
   - `update --stage N --status S [--rdm R] [--reason R]` — Advance pipeline state
   - `read` — Output current state as JSON
   - `resume-from` — Return the next step number based on current state
   This eliminates JSON construction from the LLM at every step transition and makes the resume logic deterministic and testable.

3. **Extend `scripts/check-deliverables.py` with `--stage` flag** — When `--stage 2` is passed, validate only the three release artifacts (CHANGELOG.md, deploy-checklist.md, rollback-plan.md). This reuses existing validation logic for the intermediate check at Step 2 without creating a new script.

### Architecture note

The skill already has an exceptionally clean separation between deterministic work (scripts) and orchestration work (prompts). The remaining opportunities are primarily infrastructure plumbing. If Finding 3 (state management) is implemented, consider having all existing scripts automatically update the ship state as a side effect (e.g., `check-deliverables.py` could write stage=7 to ship-state.json upon success), which would further reduce orchestration boilerplate in the prompts.
