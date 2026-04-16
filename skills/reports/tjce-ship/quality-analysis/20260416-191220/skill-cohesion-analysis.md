# Skill Cohesion Analysis — tjce-ship

**Skill:** `skills/tjce-ship`
**Date:** 2026-04-16
**Analyst:** SkillCohesionBot

---

## 1. Stage Flow Coherence

The 9-step pipeline follows a clear logical progression:

```
Pre-check (1) -> Prepare Version (2) -> Generate PML (3) -> Human Gate PML (4)
  -> APF (5) + Manual (6) [parallel, conditional] -> Checklist (7)
  -> Human Gate Deploy (8) -> Closure (9)
```

**Verdict: COHERENT**

The flow respects a natural delivery lifecycle: validate prerequisites, produce release artifacts, get human approval, generate supplementary artifacts, verify completeness, authorize deployment, close. Each step has a clear dependency on the previous one, and the two human gates are placed at exactly the right points — after artifact generation (PML) and before deployment.

The parallel execution of Steps 5 and 6 is correctly identified: APF counting and manual generation are genuinely independent of each other but both depend on PML approval (Step 4). This is a sound optimization.

**One observation:** Step 3 (Generate PML) is split from Step 2 (Prepare Version) even though both delegate to `tjce-agent-release`. This is justified because PML generation is semantically distinct from changelog/checklist/rollback production, and the PML has its own non-negotiable validation rules. The separation enables cleaner error handling and makes the gate in Step 4 easier to reason about.

---

## 2. Purpose Alignment

**Stated purpose:** Replace 5 manual phases ("Preparando Versao", "Validando PML", "Aguardando Implantacao", "Implantado", "Fechado") with a structured orchestration pipeline.

**Mapping of manual phases to steps:**

| Manual Phase | Steps | Coverage |
|---|---|---|
| Preparando Versao | 1, 2, 3 | Full — pre-check + release artifacts + PML |
| Validando PML | 4 | Full — explicit human gate |
| Aguardando Implantacao | 5, 6, 7, 8 | Full — conditional artifacts + checklist + deploy gate |
| Implantado | 8 (IMPLANTADO decision) | Full — RDM capture on confirmation |
| Fechado | 9 | Full — summary + verdict + state closure |

**Verdict: ALIGNED**

Every manual phase has a direct structural counterpart. The skill expands "Preparando Versao" into 3 substeps and "Aguardando Implantacao" into 4 substeps, which is appropriate given the automation and validation logic involved. No manual phase is orphaned or unaddressed.

The dual-mode contract (interactive + headless) is consistent with the purpose: interactive mode preserves the human decision points, headless mode enables CI/CD integration while still halting at gates.

---

## 3. Complexity Appropriateness

**Question:** Is 9 steps the right granularity for this task?

**Assessment:**

- Steps 1-3 could theoretically be collapsed into fewer steps, but the separation serves error handling: a failed pre-check (Step 1) is fundamentally different from a failed release artifact generation (Step 2) or a failed PML generation (Step 3). Each produces different error messages and recovery paths.
- Steps 5-6 are parallel and conditional — merging them would add branching complexity without reducing step count meaningfully.
- Step 7 (checklist) is a distinct verification gate that validates the outputs of Steps 2-6 collectively. Folding it into Step 8 would conflate "are artifacts complete?" with "does the human approve deployment?"
- Steps 8-9 are minimal and justified: human authorization followed by closure.

**Verdict: APPROPRIATE**

A 7-step design (merging 2+3, and 8+9) might seem leaner, but would sacrifice the clean error isolation that the current design provides. The 9-step count is not inflated — each step has a distinct responsibility and failure mode. The conditional/parallel nature of Steps 5-6 means the effective runtime path is often 7 steps in practice (skipping one or both conditionals).

**Risk note:** If future phases add more conditional artifacts, the pattern of "conditional step per artifact type" could lead to step-count inflation. Consider grouping future conditionals under a single "Generate Supplementary Artifacts" umbrella step if more than 3 conditional artifacts emerge.

---

## 4. Gap and Redundancy Detection

### Gaps Found

| ID | Gap | Severity | Recommendation |
|---|---|---|---|
| G1 | No explicit rollback step if deployment fails post-Step 8 | Medium | The `rollback-plan.md` is generated in Step 2, but no step in the pipeline addresses what happens if the PO reports a failed deployment at Step 8. The IMPLANTADO/ADIADO decisions handle pre-deployment deferral but not post-deployment failure. Consider adding a ROLLBACK decision option at Step 8, or documenting that rollback execution is out-of-scope for this orchestrator. |
| G2 | No notification mechanism for headless gate transitions | Low | When headless mode exits with code 2 at a gate, there is no defined mechanism to notify the human that action is needed. The pipeline relies on the caller to interpret exit codes. This is acceptable for CI/CD but could be documented more explicitly. |
| G3 | No timeout or expiry for pending gates | Low | If a pipeline pauses at Step 4 or Step 8, the `ship-state.json` has no expiry mechanism. A stale state file from weeks ago could be resumed without warning. Consider adding a timestamp check on resume to warn if the state is older than a configurable threshold. |
| G4 | Step 6 writes a placeholder file even when manual is not needed | Informational | When `manual_necessario == false`, a minimal file is written. This is consistent behavior for the checklist in Step 7, but should be documented as intentional (the checklist expects the file to exist). Currently the rationale is implicit. |

### Redundancies Found

| ID | Redundancy | Severity | Recommendation |
|---|---|---|---|
| R1 | Artifact existence validation in Steps 2/3/5/6 AND again in Step 7 | Informational | Each agent invocation step validates its own output, and then Step 7 re-validates all artifacts via `check-deliverables.py`. This is intentional defense-in-depth, not true redundancy. The per-step validation catches agent failures early; the Step 7 check provides a single authoritative inventory. Keep as-is. |

**Verdict: MINOR GAPS, NO HARMFUL REDUNDANCY**

The most significant gap (G1) is the absence of a post-deployment failure path. The existing redundancy (R1) is healthy defense-in-depth.

---

## 5. Dependency Graph Logic

### Explicit Dependencies

```
Step 1 -> Step 2 -> Step 3 -> Step 4 (gate)
                                 |
                          +------+------+
                          |             |
                        Step 5        Step 6    (parallel, conditional)
                          |             |
                          +------+------+
                                 |
                              Step 7 -> Step 8 (gate) -> Step 9
```

### Validation

| Dependency | Correct? | Notes |
|---|---|---|
| Step 2 depends on Step 1 | Yes | Cannot prepare version without APROVADO status and task type |
| Step 3 depends on Step 2 | Yes | PML references changelog and artifacts from Step 2 |
| Step 4 depends on Step 3 | Yes | Cannot validate a PML that does not exist |
| Steps 5/6 depend on Step 4 | Yes | No point generating APF/manual if PML is rejected |
| Step 7 depends on Steps 5+6 | Yes | Checklist must verify all conditional artifacts |
| Step 8 depends on Step 7 | Yes | Cannot authorize deployment with incomplete deliverables |
| Step 9 depends on Step 8 | Yes | Cannot close without deployment confirmation + RDM |

### Data Flow Dependencies

| Data | Produced | Consumed | Valid? |
|---|---|---|---|
| `task_type` | Step 1 (detect-task-type.py) | Steps 5, 6, 7, 9 | Yes |
| `manual_necessario` | Step 1 (detect-task-type.py) | Steps 6, 7, 9 | Yes |
| Release artifacts | Step 2 (tjce-agent-release) | Steps 3, 7, 8 | Yes |
| PML.md | Step 3 (tjce-agent-release) | Step 4 | Yes |
| APF artifacts | Step 5 (tjce-agent-apf) | Step 7 | Yes |
| Manual artifact | Step 6 (tjce-agent-docs) | Step 7 | Yes |
| ship-checklist.md | Step 7 (check-deliverables.py) | Step 8 | Yes |
| RDM number | Step 8 (human input) | Step 9 | Yes |
| ship-state.json | All steps | Resume logic | Yes |

**Verdict: CORRECT**

All dependencies are logically sound. The data flow is traceable from production to consumption. The parallel execution window (Steps 5-6) is correctly constrained — both steps are independent of each other and both depend on Step 4 completion.

---

## 6. External Skill Integration

### tjce-agent-release

| Aspect | Assessment |
|---|---|
| Invocation points | Step 2 (artifacts), Step 3 (PML), Step 4 (PML re-generation on AJUSTAR) |
| Contract clarity | Clear — headless mode, specific artifact outputs expected |
| Error handling | Covered — missing artifacts block progression, empty PML sections block gate |
| Coupling level | Low — orchestrator validates outputs, does not replicate logic |

**Quality: STRONG.** The invocation in Step 4 for PML adjustment with feedback context is well-designed: it reuses the agent's capability rather than asking the orchestrator to patch the PML.

### tjce-agent-apf

| Aspect | Assessment |
|---|---|
| Invocation points | Step 5 (conditional) |
| Contract clarity | Clear — headless mode, two output files expected |
| Error handling | Covered — missing outputs block progression |
| Coupling level | Very low — single invocation, binary skip logic |
| Conditional logic | Correct — `correcao_garantia` produces a placeholder, never invokes the agent |

**Quality: STRONG.** The zero-APF rule for warranty fixes is enforced at the orchestrator level, preventing unnecessary agent invocation.

### tjce-agent-docs

| Aspect | Assessment |
|---|---|
| Invocation points | Step 6 (conditional) |
| Contract clarity | Clear — headless mode, one output file expected |
| Error handling | Covered — missing output blocks progression |
| Coupling level | Very low — single invocation, binary skip logic |

**Quality: STRONG.** Same pattern as APF — clean conditional invocation with proper skip logic.

### Cross-Agent Observation

The three agents are invoked in a strict sequence (release -> apf || docs) with no inter-agent communication. The orchestrator is the sole mediator. This is a good design: agents remain independently testable and the orchestrator owns all control flow and validation.

**One concern:** The skill assumes all three agents support `--headless` mode but does not document the expected exit codes or output contracts of those agents within this skill's references. If an agent changes its headless contract, the orchestrator could break silently. Consider adding a brief "Agent Contracts" section to SKILL.md or a dedicated reference file that pins the expected interface of each agent.

---

## Summary

| Dimension | Rating | Notes |
|---|---|---|
| Stage flow coherence | STRONG | Logical progression, correct parallel window |
| Purpose alignment | STRONG | 1:1 mapping to all 5 manual phases |
| Complexity appropriateness | APPROPRIATE | 9 steps justified by distinct responsibilities |
| Gap & redundancy detection | MINOR GAPS | Post-deployment failure path missing (G1); no harmful redundancy |
| Dependency graph logic | CORRECT | All data and control dependencies validated |
| External skill integration | STRONG | Clean delegation, proper error handling, low coupling |

### Overall Cohesion Score: **HIGH**

The skill is well-structured with strong internal coherence. The 9-step pipeline is justified, dependencies are correct, and agent integration follows a clean orchestration pattern. The primary recommendation is to address the post-deployment failure gap (G1) and consider documenting agent interface contracts explicitly.

### Recommended Actions

1. **G1 (Medium):** Add a ROLLBACK decision option at Step 8 or explicitly document that post-deployment rollback execution is out of scope.
2. **G3 (Low):** Add a staleness warning when resuming from `ship-state.json` older than a configurable threshold (e.g., 7 days).
3. **Agent contracts (Low):** Add a reference section or file documenting the expected headless interface (exit codes, output paths, flags) for each orchestrated agent.
