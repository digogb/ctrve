# Quality Analysis Report — tjce-ship

**Skill:** `skills/tjce-ship`
**Date:** 2026-04-16
**Scanners:** 6 analysis layers + 3 pre-passes + 2 lint scans (11 total inputs)

---

## Overall Assessment: Excellent

This is a remarkably well-crafted orchestrator skill. The 9-step pipeline demonstrates strong structural integrity, exceptional token efficiency (1,210 tokens for SKILL.md), and a best-in-class progressive disclosure pattern using hub-and-spoke reference files. All 8 workflow integrity checks passed with zero issues, prompt craft scored 9.1/10, and the fail-fast ordering is optimal at every stage boundary. The primary concerns are external — a missing dependency agent (`tjce-agent-release`) that blocks the entire pipeline, and agent output path assumptions that need explicit integration contracts.

---

## What's Broken

1. **`tjce-agent-release` does not exist** — The primary dependency for Steps 2-3 is missing from the repository. The pipeline is non-functional without it. (L5: AA-01, EG-01)

2. **Agent output path mismatch** — The orchestrator expects APF artifacts at `{output_folder}/release/apf/` and manual artifacts at `{output_folder}/release/manual/`, but the existing agents (`tjce-agent-apf`, `tjce-agent-docs`) may write to different base paths. Unless the orchestrator explicitly passes an output path override, `check-deliverables.py` will fail to find artifacts. (L5: AA-02)

3. **Stale verify-verdict.json accepted without scope validation** — `check-verify-status.py` validates the verdict value but not which feature was verified. A developer who verifies Feature A and then ships Feature B will pass Step 1 with stale data. (L5: EC-01)

---

## Improvement Opportunities

### Theme 1: Incomplete External Integration Contracts

**Finding count:** 6
**Root cause:** The skill assumes specific behaviors from agents and external systems that are not formally documented or validated within its own scope.

**Findings:**
- `tjce-agent-release` referenced but does not exist (L5: AA-01, EG-01)
- Agent output paths not contractually aligned with orchestrator expectations (L5: AA-02)
- No documentation of expected agent headless interface (exit codes, output paths, flags) within this skill (L4: agent contracts observation)
- Agent exit code not checked alongside artifact existence in Step 2 (L5: EC-03)
- Verify-verdict.json scope not correlated with ship scope (L5: EC-01)
- YAML config parsed via regex instead of proper parser — fragile integration (L5: AA-07)

### Theme 2: Headless/CI Pipeline Gaps

**Finding count:** 5
**Root cause:** Headless mode handles the "run until gate" scenario well but lacks mechanisms for programmatic gate resolution and machine-readable gate identification — making true CI/CD integration incomplete.

**Findings:**
- No `--gate-response` flag for CI re-entry after human gates (L5: Headless)
- Exit code 2 does not distinguish PML gate from deployment gate (L5: AA-06)
- No timeout/watchdog for agent invocations in headless mode (L5: Headless)
- No structured error output guaranteed on exit 1 (L5: Headless)
- No notification/webhook mechanism when gates are reached (L5: missing patterns)

### Theme 3: State Management Fragility

**Finding count:** 5
**Root cause:** `ship-state.json` is the sole persistence mechanism but lacks a formal schema, atomic writes, staleness detection, and concurrency protection.

**Findings:**
- Schema never formally defined despite 8+ references across files (L5: EG-04)
- No distinction between "step started" vs "step completed" in state (L5: Archetype E)
- No staleness/expiry check on resume (L4: G3)
- No concurrency protection (file locking/PID) for simultaneous invocations (L5: EC-02)
- `--continue` does not validate that CLI args match stored state (L5: EC-05)
- State management is a prime candidate for script extraction — ~1,350-2,250 tokens per pipeline run in deterministic JSON operations (L6: Finding 3)

### Theme 4: Remaining Deterministic Work in Prompts

**Finding count:** 4
**Root cause:** While the skill already delegates major deterministic tasks to 4 excellent scripts, several intermediate validation and infrastructure operations remain as LLM work, adding ~2,100-3,450 tokens of deterministic processing per full pipeline run.

**Findings:**
- PML structural validation (placeholder/empty section detection) done by LLM instead of script — guards a non-negotiable rule (L6: Finding 1)
- Ship state checkpoint management repeated 9+ times as LLM JSON construction (L6: Finding 3)
- Release artifact intermediate check at Step 2 not scripted (L6: Finding 2)
- Agent availability pre-flight check could be scripted (L6: Finding 4)

---

## Strengths

1. **Exceptional structural integrity** — All 8 workflow integrity categories passed with zero issues. Reference files fully cover Steps 1-9 with no gaps, no overlaps, and correct progression directives forming a complete chain.

2. **Best-in-class progressive disclosure** — The hub-and-spoke pattern with 3 semantically-grouped reference files is superior to per-step splitting. Each file is independently actionable within its phase, and the routing table in SKILL.md gives the LLM the full pipeline map before loading any detail.

3. **Outstanding token efficiency** — 1,210 tokens for a 9-step orchestrator covering 3 agents, 4 scripts, 2 human gates, conditional branching, headless/interactive duality, error recovery, and state checkpointing. Zero waste patterns detected.

4. **Optimal fail-fast ordering** — Every expensive operation is preceded by a cheaper validation gate. Every human gate is preceded by automated validation. The cheap verify-status check runs first, agent pre-flight runs before any delegation, and the deliverables checklist validates before the deployment gate.

5. **Clean agent delegation boundaries** — The orchestrator never replicates agent logic. The explicit instruction "Do not replicate this logic" in reference files is an exemplary boundary marker. Agents remain independently testable.

6. **Comprehensive headless contract** — Exit codes (0/1/2) are consistently enforced across all reference files. Human gates correctly differentiate interactive vs. headless behavior. The `--continue` flag enables resume after gates.

7. **Excellent script suite** — All 4 existing scripts follow a consistent contract (JSON output, exit code discipline, `--output`/`--verbose`/`--format` flags) and all have unit tests. The skill already delegates the heaviest deterministic operations to scripts.

8. **Robust conditional logic propagation** — Task type and manual flag decisions flow consistently from detection (Step 1) through execution (Steps 5-6) to validation (Step 7) and summary (Step 9). The APF skip rule and manual conditional are enforced at every relevant point.

9. **Well-designed human gates** — The AJUSTAR feedback loop at Step 4 captures feedback, re-invokes the agent with context, and returns to validation — preventing the "stuck at gate" problem. Both gates are correctly non-automatable.

10. **Direct, imperative language** — No hedging, no meta-explanation, no identity preamble. Inegociaveis section is genuinely load-bearing, not defensive padding.

---

## Detailed Analysis

### Structure (L1 — Workflow Integrity)

**Verdict: PASS across all 8 categories**

- Frontmatter well-formed with trigger phrases in Portuguese and English
- All 7 required/domain sections present and load-bearing
- 3 reference files fully cover Steps 1-9 with correct frontmatter
- All 4 script references resolve, CLI signatures match documentation
- Output artifact table aligns with actual script producers
- Language is direct and action-oriented with no hedging
- Config integration consistent across SKILL.md, references, and scripts
- Headless contract fully specified with exit codes enforced at every decision point
- Cross-file logical consistency verified for conditionals, artifact paths, agent delegation, and parallelism

### Craft (L2 — Prompt Quality)

**Score: 9.1/10**

| Dimension | Score |
|-----------|-------|
| Overview quality | 9/10 |
| Token efficiency | 10/10 |
| Outcome vs implementation | 9/10 |
| Progressive disclosure | 10/10 |
| Self-containment | 8/10 |
| Config headers | 8/10 |
| Progression conditions | 9/10 |
| Anti-patterns | 10/10 |

Key observations:
- One compaction vulnerability: `pre-check-and-release.md` back-references SKILL.md Error Recovery section. Should be inlined.
- Minor gap: scripts not enumerated in Overview section
- Minor gap: no micro-checkpoint between Steps 2 and 3 within the reference file

### Cohesion (L4 — Skill Integration)

**Rating: HIGH**

- Stage flow is coherent with logical progression matching a natural delivery lifecycle
- 1:1 mapping to all 5 manual phases the skill replaces
- 9-step count is justified by distinct responsibilities and failure modes
- Dependency graph is correct with no cycles or transitive redundancies
- Agent integration is clean with low coupling and proper error handling
- One gap: no post-deployment rollback step if deployment fails after Step 8 (G1, Medium)
- One gap: no staleness warning on resume from old state (G3, Low)

### Efficiency (L3 — Execution Performance)

**Rating: HIGH**

- Fail-fast ordering is optimal at every stage boundary
- Steps 5+6 parallel execution correctly identified and documented
- Subagent delegation is clean with no context leakage
- Reference loading uses lazy three-stage pattern
- Minor optimization: Step 9 dual `generate-ship-summary.py` calls can be parallelized (Low)
- Minor optimization: Step 1 scripts could be chained with `&&` (Low)
- Total savings from optimizations: ~2 tool-call round-trips (~5-10 seconds)

### Experience (L5 — Enhancement Opportunities)

**Headless readiness: 7/10**

7 edge cases identified (1 critical, 2 high, 3 medium, 1 low), 5 experience gaps, 5 delight opportunities, 7 assumption audits, 5 user journey archetypes stress-tested.

Key experience gaps:
- No operational path from ADIADO to re-entry (EG-02)
- Unbounded AJUSTAR loop with no escalation (EC-04)
- No onboarding message for first-time users (Archetype B)
- Ship-state.json schema implicit (EG-04)

Delight opportunities:
- "Quick Ship" cosmetic mode for correcao_garantia (DO-01)
- Progress dashboard in interactive mode (DO-02)
- Dry run mode for pipeline preview (DO-04)

### Scripts (L6 — Script Opportunities)

**Existing scripts: Excellent (4/4 with tests)**

4 new script opportunities identified totaling ~2,100-3,450 tokens of deterministic work per full pipeline run:

1. `validate-pml.py` — PML structural validation (High, ~300-500 tokens)
2. `manage-ship-state.py` — State checkpoint manager (Medium, ~1,350-2,250 cumulative)
3. Extend `check-deliverables.py --stage 2` — Intermediate artifact check (Medium, ~100-200 tokens)
4. `check-agent-availability.py` — Agent pre-flight check (Low, ~150-200 tokens)

---

## Recommendations

### Rank 1 — Create `tjce-agent-release` or mark skill as blocked
**Impact:** Critical — pipeline is non-functional without it
**Resolves:** AA-01, EG-01, Archetype C blocker
**Action:** Either build the agent or add a prominent "DEPENDENCY NOT YET AVAILABLE" marker in SKILL.md with a tracking reference.

### Rank 2 — Formalize agent output path integration contract
**Impact:** High — prevents silent artifact path mismatches
**Resolves:** AA-02, check-deliverables.py failures
**Action:** Document explicitly whether the orchestrator passes `{output_folder}/release/` as the agent's output path, or whether agents must be parameterized to accept a custom directory. Add this to a brief "Agent Contracts" section in SKILL.md or a dedicated reference file.

### Rank 3 — Create `scripts/validate-pml.py`
**Impact:** High — guards a non-negotiable rule more reliably than LLM pattern matching
**Resolves:** L6 Finding 1, AA-03 (fragile placeholder detection), EG-03 (partially)
**Action:** ~60-line script that extracts H2/H3 sections, validates against expanded forbidden patterns, returns JSON with per-section status. Invoke at Step 3 after agent produces PML.

### Rank 4 — Create `scripts/manage-ship-state.py`
**Impact:** Medium-High — eliminates ~1,350-2,250 tokens of deterministic work per pipeline run
**Resolves:** L6 Finding 3, EG-04 (implicit schema), EC-05 (task-type mismatch on resume), Archetype E (resume ambiguity), L6 Finding 5
**Action:** State manager with `init`, `update`, `read`, `resume-from` subcommands. Enforces schema, atomic writes, two-phase state (running/completed), and CLI arg validation on resume.

### Rank 5 — Add scope validation to verify-status check
**Impact:** Medium — prevents shipping wrong feature
**Resolves:** EC-01 (stale verify-verdict.json)
**Action:** Add a `scope_hash` or timestamp comparison in `check-verify-status.py`. If `verify-verdict.json` is older than the most recent commit, warn. If a feature identifier is available, validate it matches.

### Rank 6 — Inline error handling rule in `pre-check-and-release.md`
**Impact:** Medium — compaction survival
**Resolves:** L2 self-containment gap, back-reference vulnerability
**Action:** Replace "report and halt per the Error Recovery section in SKILL.md" with the actual rule: "report with instructions to verify agent is installed and halt — exit 1."

### Rank 7 — Add `--gate-response` flag for headless CI re-entry
**Impact:** Medium — enables true CI/CD integration
**Resolves:** Headless gaps (no programmatic gate resolution), AA-06 (gate identification), Archetype C pain points
**Action:** Accept `--gate-response approved|ajustar|implantado|adiado [--rdm RDM-NNN]` on `--continue`. Write `pending_gate` field to ship-state.json at exit 2.

### Rank 8 — Add AJUSTAR iteration limit with escalation
**Impact:** Low-Medium — prevents unbounded loops
**Resolves:** EC-04
**Action:** After 3 AJUSTAR cycles, present escalation prompt: continue, edit manually, or abort. Write iteration count to ship-state.json.

### Rank 9 — Extend `check-deliverables.py` with `--stage` flag
**Impact:** Low — design consistency between Steps 2 and 7
**Resolves:** L6 Finding 2
**Action:** When `--stage 2` is passed, validate only the three release artifacts. Near-zero effort — reuses existing validation logic.

### Rank 10 — Add post-deployment failure path documentation
**Impact:** Low — operational completeness
**Resolves:** L4 G1 (no rollback step)
**Action:** Add ROLLBACK as a third option at Step 8, or explicitly document that post-deployment rollback execution is out-of-scope for this orchestrator and refer to the rollback-plan.md artifact.
