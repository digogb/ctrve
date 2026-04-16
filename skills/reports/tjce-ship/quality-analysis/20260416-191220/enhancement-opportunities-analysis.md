# Enhancement Opportunities Analysis — tjce-ship

**Skill:** `skills/tjce-ship`
**Analyzer:** DreamBot
**Date:** 2026-04-16
**Scope:** Edge cases, experience gaps, delight opportunities, assumption audit, headless completeness, facilitative patterns, user journey stress tests

---

## 1. Edge Cases — What Breaks When Users Do the Unexpected

### EC-01: Stale verify-verdict.json from a previous feature
**Severity:** Critical
**Scenario:** Developer runs `/tjce-verify` for Feature A, gets APROVADO. Then pivots to Feature B without re-running verify. Invokes `/tjce-ship`. Step 1 passes because `verify-verdict.json` still shows APROVADO — but it belongs to a different feature.
**Why it breaks:** `check-verify-status.py` checks only the existence and value of the verdict. It has no concept of *which* feature was verified. There is no correlation between verify and ship scopes.
**Recommendation:** Add a `feature_id` or `scope_hash` field to `verify-verdict.json` (written by tjce-verify) and validate it matches the current ship scope in Step 1. At minimum, compare timestamps: if `verify-verdict.json` is older than the most recent commit, warn.

### EC-02: Concurrent ship invocations on the same project
**Severity:** High
**Scenario:** Two terminals, or a CI pipeline and a developer, both invoke `/tjce-ship` simultaneously. Both read `ship-state.json`, both proceed, both write artifacts — race condition on state.
**Why it breaks:** There is no file-level locking or PID tracking on `ship-state.json`.
**Recommendation:** Write a `ship-state.json` lock field containing PID and hostname at step 1. On activation, if a lock exists and the process is still alive, refuse to start. If the process is dead (stale lock), offer to claim.

### EC-03: Agent produces artifacts but returns non-zero exit code
**Severity:** High
**Scenario:** `tjce-agent-release --headless` writes `CHANGELOG.md` and `deploy-checklist.md` but crashes before `rollback-plan.md`. The orchestrator's validation in Step 2 catches the missing file. But what if the agent writes all three files and *then* exits 1 because of an internal warning? The orchestrator currently checks only file existence, not the agent's exit code.
**Why it breaks:** Step 2 checks "artifacts exist" but does not check "agent returned success." A partially-correct agent run could produce artifacts with truncated content that pass existence checks.
**Recommendation:** Check both: (a) agent exit code == 0, AND (b) all expected artifacts exist and are non-empty. Treat exit code != 0 as a warning that requires artifact content validation beyond existence.

### EC-04: PML AJUSTAR loop with no termination bound
**Severity:** Medium
**Scenario:** In Step 4 interactive mode, the DevOps reviewer keeps saying AJUSTAR. Each time, the orchestrator re-invokes `tjce-agent-release --headless pml` with feedback. If the agent keeps producing unsatisfactory output, this loops forever.
**Why it breaks:** No iteration limit or escalation path defined.
**Recommendation:** After 3 AJUSTAR cycles, present an escalation prompt: "O PML foi ajustado 3 vezes sem aprovacao. Deseja: (a) continuar ajustando, (b) editar o PML manualmente, (c) abortar o pipeline?" Write the iteration count to `ship-state.json` for resume awareness.

### EC-05: `--continue` invoked with wrong `--task-type`
**Severity:** Medium
**Scenario:** Original run used `--task-type nova_funcionalidade`. Resume run uses `--continue --task-type correcao_garantia`. The conditional logic for steps 5-6 now operates under a different task type than the artifacts already produced.
**Why it breaks:** `ship-state.json` stores the step but the SKILL.md does not specify that `task_type` stored in state should be compared against the CLI argument on resume.
**Recommendation:** Store `task_type` and `manual_necessario` in `ship-state.json` (the SKILL.md mentions this but the contract is implicit). On `--continue`, validate that CLI args match stored state. If mismatch, refuse and explain.

### EC-06: `detect-task-type.py` infers "mudanca" but the actual task is "nova_funcionalidade"
**Severity:** Medium
**Scenario:** The inference heuristic in `_infer_from_config` reads `config.json` which has `task_type: mudanca` from a previous sprint. The current task is actually a new feature. In headless mode, there is no confirmation step — the wrong type silently propagates, causing APF counting to use enhancement mode instead of nova mode.
**Why it breaks:** The config.json is not scoped per feature/sprint. Stale configuration silently wins.
**Recommendation:** In headless mode, if task type was inferred (not explicit CLI), include a `detection_confidence: "inferred"` field in the JSON output and log a warning to stderr. The orchestrator should treat inferred types with lower confidence and, in interactive mode, always confirm.

### EC-07: Partial artifact directory on resume
**Severity:** Low
**Scenario:** Ship runs to Step 5, APF agent creates `apf/` directory but crashes before writing `resumo-apf.md`. Resume picks up at Step 5 (or 6). If the orchestrator does not clear partial artifacts before re-invoking the agent, the agent might see a half-populated directory and behave unexpectedly.
**Recommendation:** On resume, if the step being resumed is an agent invocation step, validate that expected outputs either all exist (skip) or none exist (re-run). If partial, clean the partial outputs before re-invoking.

---

## 2. Experience Gaps — Dead-Ends, Assumption Walls, Missing Recovery

### EG-01: tjce-agent-release does not exist yet
**Severity:** Critical (blocking)
**Detail:** The skill references `tjce-agent-release` as its primary agent for Steps 2 and 3. No `skills/tjce-agent-release/SKILL.md` exists in the repository. This is the most critical dependency: the pipeline cannot execute at all without it.
**Impact:** Any attempt to run the ship pipeline will hit the "Agent Unavailability" error at Step 1 preflight, with no recovery path except "go build the agent."
**Recommendation:** Either (a) create `tjce-agent-release` before shipping this skill, or (b) add a clear "NOT YET AVAILABLE" marker in the SKILL.md with a tracking reference, so users are not surprised by a broken pipeline.

### EG-02: No path from ADIADO back to IMPLANTADO
**Severity:** High
**Detail:** Step 8 allows the PO to say ADIADO, recording a reason and expected date. The skill then exits. But there is no documented re-entry mechanism specifically for ADIADO. The `--continue` flag will resume from step 8, but the user experience gap is: when the expected date arrives, who or what triggers the re-entry? There is no notification, no reminder, no integration with any calendar or ticketing system.
**Recovery path present?** Partially. `--continue` works mechanically, but there is no operational guidance.
**Recommendation:** When ADIADO is recorded, output a concrete next-step instruction: "Execute `/tjce-ship --continue` quando a implantacao for autorizada. Data esperada: {data}." If integrated with CI, suggest a scheduled re-trigger.

### EG-03: No guidance when agents produce partially-correct output
**Severity:** Medium
**Detail:** The Error Recovery section distinguishes "bad output" vs "crashed" but provides no guidance for "output exists but is questionable." For example, if `tjce-agent-release` produces a PML that technically has no empty sections but the content is vague or clearly hallucinated, the only guard is the human gate at Step 4. But between Step 3 and Step 4, there is no automated quality check on PML *content quality* — only structural checks (non-empty, no placeholders).
**Recommendation:** Add a PML structural validation script (e.g., `validate-pml-structure.py`) that checks: minimum section lengths, presence of specific expected subsections (migrations, config changes, rollback procedures), no repeated boilerplate paragraphs. This does not replace human judgment but catches obvious agent failures before presenting to the gate.

### EG-04: Ship-state.json schema is implicit
**Severity:** Medium
**Detail:** `ship-state.json` is mentioned 8 times across the skill files, but its schema is never formally defined. Different steps write different fields (stage, status, timestamp, task_type, flags, rdm, reason, expected_date...). Without a canonical schema, resume logic and external tooling must guess at the structure.
**Recommendation:** Define a `ship-state.schema.json` or at minimum document the full schema in the SKILL.md Output Artifacts section. Include all possible fields, their types, and which step writes them.

### EG-05: No way to skip to a specific step
**Severity:** Low
**Detail:** If a developer knows that Steps 1-6 completed successfully (e.g., from a previous run that crashed at Step 7), they must use `--continue` which reads state. But if `ship-state.json` is corrupted or missing, they have no way to say "start from Step 7." There is no `--from-step N` flag.
**Recommendation:** Add `--from-step N` with appropriate warnings: "Pular steps pode resultar em artefatos inconsistentes. Confirma?" This is a power-user escape hatch, not a default workflow.

---

## 3. Delight Opportunities — Quick-Win Modes, Smart Defaults

### DO-01: "Quick Ship" mode for correcao_garantia
**Scenario:** Warranty fixes are the simplest path: APF = 0, no manual. Steps 5 and 6 are trivially skipped. The pipeline could offer a fast path: `--quick` or auto-detect `correcao_garantia` and announce "Modo rapido ativado — APF e manual nao aplicaveis."
**Value:** Reduces cognitive load. The user sees the pipeline acknowledge the simplicity rather than watching it methodically skip steps.
**Implementation:** In interactive mode, after detecting `correcao_garantia`, display: "Correcao em Garantia detectada. Pipeline simplificado: Steps 5-6 serao pulados automaticamente (APF = 0, manual nao aplicavel)." This is cosmetic but signals awareness.

### DO-02: Progress dashboard in interactive mode
**Scenario:** The pipeline has 9 steps. In a long interactive session, the user loses track of where they are.
**Value:** A persistent progress indicator (even textual) orients the user.
**Implementation:** Before each step, output a progress line:
```
[Step 3/9] Gerar PML ==========>------------ 33%
```
Trivial to implement, high orientation value.

### DO-03: Elapsed time tracking per step
**Scenario:** Agent invocations (Steps 2, 3, 5, 6) can take significant time. After completion, knowing "Step 2 took 47 seconds" helps calibrate expectations and diagnose performance.
**Value:** `ship-state.json` already stores timestamps per step. Surfacing elapsed time in the summary makes operational performance visible.
**Implementation:** In `ship-summary.md`, add a "Pipeline Timing" section showing elapsed time per step. The data is already available in checkpoints.

### DO-04: "Dry run" mode
**Scenario:** A tech lead wants to see what the ship pipeline *would* do without actually invoking agents or writing artifacts. For planning, estimation, or debugging.
**Value:** Low-risk pipeline preview. Shows which agents will be invoked, which steps will be skipped, and which gates will be hit.
**Implementation:** `--dry-run` flag: runs Step 1 (pre-check, detect type, agent availability) and then outputs a plan without executing. Exit 0 with a plan summary.

### DO-05: Smart defaults for RDM format
**Scenario:** Step 8 captures an RDM number from the PO. If the organization uses a predictable format (e.g., `RDM-YYYY-NNN`), suggest the next sequential number.
**Value:** Reduces typing and typos for a formal tracking number.
**Implementation:** Scan `ship-state.json` history or a project-level registry for the last RDM, suggest increment. Low effort, high polish.

---

## 4. Assumption Audit — What Assumptions Might Be Wrong

### AA-01: Assumption: tjce-agent-release exists and has a --headless flag
**Status:** FALSE
**Evidence:** `skills/tjce-agent-release/SKILL.md` does not exist in the repository. The pipeline depends entirely on this agent for Steps 2 and 3. This is the single biggest risk to the skill's viability.
**Impact:** Pipeline is non-functional until this agent is built.

### AA-02: Assumption: All three agents write to `{output_folder}/release/`
**Status:** PARTIALLY VALIDATED
**Evidence:** `tjce-agent-apf` writes to `{output_folder}/` (its own base), not `{output_folder}/release/`. The ship pipeline expects APF artifacts at `{output_folder}/release/apf/`. The agent's headless contract does not specify writing to a subdirectory of `release/`. Similarly, `tjce-agent-docs` writes to `{output_folder}/manual/`, not `{output_folder}/release/manual/`.
**Impact:** Unless the orchestrator explicitly passes an output path override, agents will write to different locations than where `check-deliverables.py` expects them.
**Recommendation:** Either (a) the orchestrator must set the agent's output path to `{output_folder}/release/` or copy outputs after agent completion, or (b) the agents must be parameterized to accept a custom output directory. Document this integration contract explicitly.

### AA-03: Assumption: PML sections can be validated by checking for "TODO" or "a definir"
**Status:** FRAGILE
**Evidence:** Step 3 checks for "placeholders, TODO, a definir, or empty sections." But an LLM agent might generate placeholder-like content that does not match these literal strings — e.g., "Detalhes a serem confirmados", "Ver com o time de infra", "[pendente]", or simply vague filler text that is technically non-empty.
**Impact:** Hollow PMLs could pass automated validation and reach the human gate, wasting the DevOps reviewer's time.
**Recommendation:** Expand the placeholder detection list and consider a minimum word count per section. Add patterns like: "a ser definido", "pendente", "confirmar com", "[...]", "lorem ipsum", "exemplo".

### AA-04: Assumption: Human gates are always reached by the same person
**Status:** QUESTIONABLE
**Evidence:** Step 4 is validated by "DevOps / Gerente de Configuracao" and Step 8 by "PO". But in headless/CI workflows, the re-entry via `--continue` does not authenticate or verify *who* is resuming. Any user with access to the CLI can confirm either gate.
**Impact:** In an audit context, there is no proof that the right role approved the right gate.
**Recommendation:** For formal environments, capture the approver's identity (at minimum, a name typed at the prompt; at best, integration with git config user.name or an SSO token). Write it to `ship-state.json` as `pml_approved_by` and `deployment_confirmed_by`.

### AA-05: Assumption: Steps 5 and 6 are truly independent and safe to parallelize
**Status:** TRUE with caveat
**Evidence:** APF counting and manual generation use different input artifacts (requirements + data model vs. user stories + messages + screens) and write to different output directories. They are logically independent.
**Caveat:** If both agents read `config.yaml` and one of them modifies a shared temp file, there could be a race condition. The current agent contracts suggest read-only access to config, so this is low risk but should be documented as a constraint.

### AA-06: Assumption: Headless mode exit code 2 is sufficient for CI orchestration
**Status:** MOSTLY TRUE but incomplete
**Evidence:** Exit 2 means "waiting for human gate." CI systems can detect this and pause. But there is no machine-readable indication of *which* gate is pending (PML vs. deployment). A CI pipeline needs to know which approval to request.
**Recommendation:** `ship-verdict.json` (or a dedicated `ship-status.json`) written at exit should include `pending_gate: "pml_validation" | "deployment_confirmation"` so CI systems can route the approval request to the right team.

### AA-07: Assumption: The YAML config parser (regex-based) is reliable
**Status:** FRAGILE
**Evidence:** `detect-task-type.py` uses `re.search(r"task_type\s*:\s*(\S+)", content)` to parse YAML. This will fail on: multi-line values, quoted values with spaces, comments on the same line, nested keys (e.g., `ship: { task_type: mudanca }`).
**Impact:** Silent misparse could lead to wrong task type inference.
**Recommendation:** Use a proper YAML parser (`pyyaml` or `ruamel.yaml`) or at minimum document that the config must use flat `key: value` format.

---

## 5. Headless Potential — Completeness Assessment

### Overall Headless Readiness: 7/10

**What is well-defined:**
- Exit codes (0, 1, 2) are clearly specified with distinct semantics
- `--headless` flag is documented in SKILL.md and passed through to agents
- `--continue` flag for re-entry after human gates
- Artifact paths are deterministic and documented
- `ship-verdict.json` provides structured output for automation

**What is missing or underspecified:**

| Gap | Severity | Detail |
|-----|----------|--------|
| No `--gate-response` flag for CI re-entry | High | To resume past a gate in CI, you need `--continue`. But there is no way to *programmatically pass the gate decision* (e.g., `--gate-response approved --rdm RDM-2024-001`). The user must interact or hack `ship-state.json` manually. |
| No machine-readable pending gate identifier | Medium | Exit 2 does not distinguish PML gate from deployment gate. CI must parse `ship-state.json` to determine which gate. |
| No `--timeout` for agent invocations | Medium | In headless/CI mode, a hung agent invocation will block indefinitely. No timeout or watchdog mechanism. |
| No structured error output on exit 1 | Low | Exit 1 means "blocked" but there is no guaranteed structured error file. Some scripts write JSON, but agent crashes may not. |
| ship-state.json is the sole resume mechanism | Low | If the file is corrupted or deleted, headless resume is impossible. No backup or recovery. |

**Recommendation for full headless CI pipeline:**
```
# Phase 1: Run until first gate
tjce-ship --headless --task-type nova_funcionalidade
# exits 2, writes ship-state.json with pending_gate

# Phase 2: External approval (e.g., Slack bot, JIRA transition)
# ...approval received...

# Phase 3: Resume with gate response
tjce-ship --headless --continue --gate-response approved

# Phase 4: Hits second gate, exits 2 again

# Phase 5: Deployment confirmed externally
tjce-ship --headless --continue --gate-response implantado --rdm RDM-2024-042
# exits 0
```

This flow requires `--gate-response` which does not exist yet.

---

## 6. Facilitative Workflow Patterns — Present vs Missing

### Present Patterns

| Pattern | Where | Assessment |
|---------|-------|------------|
| **Sequential pipeline with checkpoints** | Steps 1-9 with ship-state.json | Well-implemented. Clear step ordering with state persistence. |
| **Conditional branching** | Steps 5-6 based on task_type and manual flag | Clean: skip APF for garantia, skip manual unless flagged. Parallel execution when both apply. |
| **Human-in-the-loop gates** | Steps 4 and 8 | Correctly non-automatable. Two distinct approval roles (DevOps, PO). |
| **Fail-fast with diagnostics** | Pre-check (Step 1), artifact validation (Steps 2-3, 7) | Scripts return structured JSON with findings, severity, and fix suggestions. |
| **Agent delegation** | Steps 2, 3, 5, 6 | Clean orchestrator pattern: invoke agent, validate output, do not replicate logic. |
| **Dual-mode (interactive/headless)** | All steps | Consistently documented for both modes. |

### Missing Patterns

| Pattern | Value | Recommendation |
|---------|-------|----------------|
| **Rollback / undo** | High | No mechanism to "undo" a completed step. If Step 3 produces a bad PML and the user wants to redo Step 2 (changelog was wrong), they must restart the entire pipeline or manually delete artifacts and hack ship-state.json. Add `--redo-step N` to re-execute a specific step. |
| **Approval audit trail** | High | Gate decisions are stored in ship-state.json but without approver identity, timestamp of decision (vs. timestamp of state write), or the actual feedback given during AJUSTAR cycles. For a judicial system, audit trail is likely a regulatory requirement. |
| **Notification / webhook** | Medium | When a gate is reached in headless mode, exit 2 is the only signal. No webhook, no email, no Slack notification. CI pipelines can detect the exit code, but standalone headless runs are silent. Add `--notify-url <webhook>` for gate-reached events. |
| **Artifact versioning** | Medium | If Step 3 is re-run (AJUSTAR), the new PML overwrites the old one. There is no version history. For audit and comparison, retain `PML.v1.md`, `PML.v2.md` or use a `pml-history/` directory. |
| **Pipeline introspection** | Low | No `--status` flag to query the current pipeline state without executing. Users must read ship-state.json manually. Add `tjce-ship --status` that reads and formats the state. |
| **Partial success / degraded completion** | Low | The pipeline is all-or-nothing: either FECHADO or stuck. There is no concept of "completed with warnings" (e.g., manual generated but with TELA NAO IDENTIFICADA marks). The summary could distinguish FECHADO from FECHADO_COM_RESSALVAS. |

---

## 7. User Journey Stress Tests

### Archetype A: The Seasoned DevOps Engineer (Interactive, Happy Path)
**Profile:** Knows the process, has all prerequisites, wants to move fast.
**Journey:**
1. Runs `/tjce-ship`. Config loaded, feature confirmed. **Smooth.**
2. Step 1 passes (verify was done yesterday). **Smooth.**
3. Steps 2-3: agent invoked, artifacts produced. **Smooth.**
4. Step 4: Reviews PML, approves immediately. **Smooth.**
5. Steps 5-6: APF counted, manual skipped (not flagged). **Smooth.**
6. Step 7: Checklist green. **Smooth.**
7. Step 8: PO approves, provides RDM. **Smooth.**
8. Step 9: Summary generated. **Smooth.**
**Pain points:** None on happy path. This archetype is well-served.
**Micro-optimization:** Steps 2-3 are currently sequential (first release artifacts, then PML). Since PML is a separate agent invocation (`--headless pml`), could these two invocations be parallelized? The PML reads changelog (produced in Step 2), so no — the dependency is correct.

### Archetype B: The Junior Dev Doing Their First Ship (Interactive, Confused)
**Profile:** Never run the pipeline before. Does not know what PML means. Might not have run verify.
**Journey:**
1. Runs `/tjce-ship`. Config loaded, asked to confirm feature. **Confusing — "qual feature?" They might not know what to answer.**
2. Step 1: verify-verdict.json not found. Pipeline says "Execute /tjce-verify primeiro" and exits. **Dead-end. The user might not know what tjce-verify is or how to use it.**
**Pain points:**
- No onboarding message explaining the pipeline before starting
- Error messages assume familiarity with the process vocabulary (PML, APF, RDM)
- No link to documentation or help command
**Recommendation:** Add an introductory message on first activation: "Este pipeline prepara a entrega (release) do seu projeto em 9 etapas: preparacao de versao, validacao, geracao de artefatos e fechamento. Pre-requisito: a verificacao (/tjce-verify) deve estar aprovada." Consider a `--explain` flag that describes each step before executing.

### Archetype C: The CI Pipeline (Headless, Multi-Stage)
**Profile:** Automated system. Runs headless. Needs deterministic behavior.
**Journey:**
1. Runs `tjce-ship --headless --task-type nova_funcionalidade`. Config defaults applied. **Smooth.**
2. Step 1 passes. Agents available (except tjce-agent-release does not exist — **BLOCKED at preflight**).
**Critical blocker:** The pipeline cannot proceed in CI because the primary agent is missing.
**Assuming the agent existed:**
3. Steps 2-3 complete. Step 4: exits with code 2. `ship-state.json` written. **Smooth but: how does CI know to request PML approval? Only by parsing ship-state.json.**
4. Human approves PML externally. CI runs `tjce-ship --headless --continue`. **Gap: no way to pass the approval decision programmatically. CI must either manipulate ship-state.json or there is an undocumented mechanism.**
5. Steps 5-7 complete. Step 8: exits with code 2 again. **Same gap: how to pass IMPLANTADO + RDM programmatically.**
**Pain points:**
- Two undocumented manual interventions in an "automated" pipeline
- No webhook/callback mechanism for gate notifications
- No programmatic gate-response flag
**Recommendation:** The `--gate-response` flag (see Section 5) is essential for true CI integration. Without it, headless mode is "headless until a gate, then manual."

### Archetype D: The Emergency Warranty Fix Developer (correcao_garantia)
**Profile:** Fixing a production bug under time pressure. Wants the fastest possible path to deployment.
**Journey:**
1. Runs `/tjce-ship --task-type correcao_garantia`. **Smooth.**
2. Step 1 passes. Agent preflight: only `tjce-agent-release` needed (APF skipped, manual not flagged). **Smooth.**
3. Steps 2-3 complete. **Must still generate full PML for a warranty fix. Is that appropriate? A production hotfix might need a lighter PML.**
4. Step 4: DevOps must still formally approve PML. **Friction for an emergency fix. No "expedited approval" path.**
5. Steps 5-6 skipped (APF = 0, no manual). **Smooth — this is the fast path working as designed.**
6. Step 7: Checklist green. **Smooth.**
7. Step 8: PO must approve deployment. **Second gate for an emergency fix. Total: 2 mandatory gates even for hotfixes.**
8. Step 9: Closure. **Smooth.**
**Pain points:**
- Two mandatory human gates create latency for emergency fixes
- No "emergency" or "expedited" mode that reduces gate requirements
- PML generation for a hotfix may be overkill (rollback plan is critical, but full PML may not be)
**Recommendation:** Consider an `--urgency critical` flag that: (a) flags the PML as expedited, (b) allows the same person to approve both gates in sequence rather than requiring two distinct roles, (c) adds a "post-hoc review" marker so the abbreviated process is audited later. This is a policy decision, not a technical one — document the trade-off even if the decision is "no, both gates are always required."

### Archetype E: The Resuming User (State Recovery After Crash)
**Profile:** Pipeline crashed or was interrupted at Step 5. Returns hours later.
**Journey:**
1. Runs `/tjce-ship`. Detects `ship-state.json`. Offers to resume. **Smooth.**
2. User accepts resume. Pipeline reads state: step 5 was in progress. **What happens next depends on interpretation: does it re-run Step 5 or skip to Step 6?**
**Ambiguity:** The SKILL.md says "update ship-state.json with current step" after completion. If the crash happened *during* Step 5 (agent was invoked but never returned), the state says step=4 (last completed) or step=5 (in progress)? This is not specified.
**Pain points:**
- No distinction between "step N completed" and "step N started" in state
- Partial artifacts from crashed step may confuse the re-run (see EC-07)
- No integrity check on ship-state.json itself (could be truncated by a crash during write)
**Recommendation:** Use two-phase state: `{current_step: 5, step_status: "running" | "completed"}`. On resume, if `step_status == "running"`, clean partial outputs and re-run. If `step_status == "completed"`, advance to next step. Write state atomically (write to `.ship-state.json.tmp` then rename).

---

## Summary of Recommendations by Priority

### Must-Fix (blocks correct operation)

| ID | Issue | Section |
|----|-------|---------|
| AA-01 | tjce-agent-release does not exist | Assumption Audit |
| AA-02 | Agent output paths do not match orchestrator expectations | Assumption Audit |
| EC-01 | Stale verify scope not validated | Edge Cases |

### Should-Fix (prevents significant user pain)

| ID | Issue | Section |
|----|-------|---------|
| EG-02 | No operational path from ADIADO to re-entry | Experience Gaps |
| EC-04 | Unbounded AJUSTAR loop | Edge Cases |
| EC-05 | --continue with mismatched task-type | Edge Cases |
| AA-06 | Headless exit 2 does not identify which gate | Assumption Audit |
| Headless | No --gate-response for CI re-entry | Headless Potential |
| EG-04 | ship-state.json schema undefined | Experience Gaps |
| Missing | Approval audit trail (approver identity) | Facilitative Patterns |

### Nice-to-Have (polish and delight)

| ID | Issue | Section |
|----|-------|---------|
| DO-01 | Quick Ship cosmetic for correcao_garantia | Delight |
| DO-02 | Progress dashboard | Delight |
| DO-03 | Elapsed time tracking | Delight |
| DO-04 | Dry run mode | Delight |
| Missing | --status introspection flag | Facilitative Patterns |
| Missing | Artifact versioning for AJUSTAR cycles | Facilitative Patterns |

---

*Analysis complete. 7 edge cases, 5 experience gaps, 5 delight opportunities, 7 assumption audits, 5 headless gaps, 6 missing workflow patterns, and 5 user journey stress tests evaluated.*
