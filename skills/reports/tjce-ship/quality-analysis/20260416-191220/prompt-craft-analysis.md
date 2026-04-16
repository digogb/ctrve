# Prompt Craft Analysis — tjce-ship

**Skill:** `skills/tjce-ship`
**Date:** 2026-04-16
**Type:** Complex workflow orchestrator (SHIP phase)
**Pattern:** SKILL.md hub + 3 reference files (progressive disclosure)

---

## 1. Overview Quality and Completeness

**Rating: Excellent**

The Overview section (16 lines) packs high information density without bloat:

- Opens with a one-sentence purpose statement that anchors the orchestrator in the broader pipeline ("fase SHIP da Esteira de Desenvolvimento do TJCE").
- Immediately names the three delegated agents and their responsibilities. This is critical for an orchestrator — the LLM must know *what it does not do itself*.
- States the pre-requisite (`/tjce-verify` concluido com status APROVADO) upfront, preventing premature execution.
- Args and mode contracts (`--headless`, `--task-type`, `--manual`) are declared at activation scope, not buried in reference files.

One minor gap: the Overview lists the three agents but does not name the four deterministic scripts. The scripts surface only in reference files and the Output Artifacts table. For an orchestrator, knowing the full cast of external dependencies at overview level would strengthen the mental model. However, this is a judgment call — the scripts are implementation detail while agents are architectural peers.

**Frontmatter** is well-formed with trigger phrases in the description. The triggers cover both Portuguese ("preparar release", "gerar PML", "fechar demanda") and English-adjacent ("executar ship"), matching likely user vocabulary.

## 2. Token Efficiency

**Rating: Excellent (0 waste patterns)**

| Metric | Value | Assessment |
|--------|-------|------------|
| SKILL.md tokens | ~1210 | Lean for a 9-step orchestrator |
| Waste patterns | 0 | Clean |
| Back references | 0 | No redundant cross-linking |
| Total reference files | 3 | ~600-700 tokens each (estimated) |
| Tables | 2 in SKILL.md | High-density format |

The entire SKILL.md is 91 lines for a workflow covering 9 steps, 3 agents, 4 scripts, 2 human gates, conditional branching, headless/interactive duality, error recovery, and a state checkpoint system. This is remarkably compact.

**No filler detected.** Every section carries behavioral weight:
- "Inegociaveis" is not defensive padding — it encodes hard constraints that override default agent behavior (e.g., "APF = 0 automatico para Correcao em Garantia — nunca invocar tjce-agent-apf").
- "Error Recovery" distinguishes two failure classes (bad output vs crash) with distinct handling — this is load-bearing, not defensive.
- The Output Artifacts table doubles as a verification contract (what must exist, who produces it, when).

## 3. Outcome vs Implementation Balance

**Rating: Strong with one observation**

The SKILL.md stays firmly at the **outcome/contract level**:
- Declares *what* each step group produces, not *how*.
- Execution Flow table maps step ranges to reference files with blocking conditions — pure orchestration logic.
- Error Recovery defines behavioral categories, not code paths.
- Headless Contract specifies exit codes and output locations — an interface contract.

The reference files appropriately shift toward **implementation**:
- Exact script invocations with argument patterns.
- Validation criteria for agent outputs (file exists, no empty sections, no placeholders).
- Decision tables for human gates (APROVADO/AJUSTAR, IMPLANTADO/ADIADO).

**Observation:** The reference files specify orchestration mechanics (invoke agent, validate output, proceed/block) without leaking into the agents' internal logic. The line "Do not replicate this logic" in `pre-check-and-release.md` Step 2 is an excellent boundary marker — it tells the LLM its role stops at delegation.

## 4. Progressive Disclosure Usage

**Rating: Excellent — best-in-class for this pattern**

The skill uses a **hub-and-spoke model** with explicit load instructions:

```
| Steps 1-3 | Load references/pre-check-and-release.md | ...
| Steps 4-7 | Load references/validation-and-artifacts.md | ...
| Steps 8-9 | Load references/deployment-and-closure.md | ...
```

Each reference file ends with an explicit **Progression** directive ("Load `references/...`"), creating a clear chain. This is the correct pattern for context-window management: the LLM loads only the active phase's instructions.

**Strengths of this design:**
- The hub table in SKILL.md gives the LLM a full mental map of the pipeline before loading any detail.
- Reference files are scoped to logical phase boundaries (pre-work, validation, closure) rather than arbitrary splits.
- No reference file needs to know about the contents of another — they are independently actionable within their phase.

**Comparison to numbered-file pattern:** This approach is superior for workflows with distinct phases because the grouping is semantic (3 files for 3 phases) rather than mechanical (1 file per step). A 9-file structure would have been fragmented and harder to maintain.

## 5. Self-Containment of Reference Files (Context Compaction Survival)

**Rating: Strong with minor dependency**

Each reference file has its own YAML frontmatter with name and description, which aids identification after compaction.

**Self-containment analysis:**

| File | Self-contained? | External dependencies |
|------|----------------|----------------------|
| `pre-check-and-release.md` | Mostly | References "Error Recovery section in SKILL.md" once (Step 1 agent availability). Uses `{output_folder}` placeholder established in SKILL.md. |
| `validation-and-artifacts.md` | Yes | Uses `{output_folder}`, `{task_type}`, `manual_necessario` — all established in prior steps, but the file re-states the conditions inline ("task_type != correcao_garantia"). |
| `deployment-and-closure.md` | Yes | Uses `{output_folder}`, `{task_type}`, `{rdm_number}` — all from state context. Fully self-contained for its phase. |

The back-reference in `pre-check-and-release.md` to "the Error Recovery section in SKILL.md" is the only compaction vulnerability. If SKILL.md gets compacted away while the reference file is active, the LLM loses the error handling taxonomy. **Recommendation:** Inline the relevant error handling rule directly in the reference file ("If any required agent is unavailable, report with instructions to verify it is installed and halt — exit 1"), eliminating the cross-reference.

The conditional logic in `validation-and-artifacts.md` is exemplary: it re-states the conditions for APF skip and manual skip inline, so the file operates independently even if the prior reference and SKILL.md context have been evicted.

## 6. Config Headers in Reference Files

**Rating: Present and adequate**

All three reference files have YAML frontmatter:

```yaml
---
name: pre-check-and-release
description: Steps 1-3 — Verify APROVADO status, detect task type, prepare version, and generate PML.
---
```

The descriptions are functional — they state the step range and purpose. This enables automated tooling and helps the LLM identify files during compaction recovery.

**Minor improvement opportunity:** Adding a `depends_on` or `requires` field to the frontmatter (e.g., `requires: [output_folder, task_type]`) would make the data contract between phases machine-readable. This is not a deficiency — it is an optimization for future tooling.

## 7. Progression Conditions

**Rating: Strong**

Each phase has clear blocking conditions stated in the Execution Flow table:

| Phase | Block condition |
|-------|----------------|
| Steps 1-3 | "Verify nao aprovado" |
| Steps 4-7 | "PML rejeitado OU artefatos faltando" |
| Steps 8-9 | "Implantacao nao confirmada" |

Within reference files, progression is explicit:
- `pre-check-and-release.md` ends with: "**Progression:** Load `references/validation-and-artifacts.md`."
- `validation-and-artifacts.md` ends with: "**Progression:** Load `references/deployment-and-closure.md`."
- `deployment-and-closure.md` ends with: "**Pipeline complete.** Demanda fechada." — a terminal marker.

**Inter-step gates are well-defined:**
- Step 1 blocks on verify status (script-enforced).
- Step 4 blocks on human PML approval (gate with AJUSTAR loop).
- Step 7 blocks on missing artifacts (script-enforced checklist).
- Step 8 blocks on human deployment confirmation.

The AJUSTAR loop in Step 4 is particularly well-designed — it captures feedback, re-invokes the agent with context, and returns to validation. This prevents the "stuck at gate" problem.

**One gap:** There is no explicit progression condition between Step 2 and Step 3 within the reference file. The text implies sequential execution (Step 2 validates artifacts, Step 3 proceeds), but the blocking condition is embedded in prose ("If any artifact is missing, treat as agent failure — do not proceed") rather than a structured gate. This is acceptable for within-file flow but could be clearer with a brief checkpoint marker.

## 8. Anti-Pattern Analysis

**Detected: None significant**

| Anti-pattern | Present? | Notes |
|-------------|----------|-------|
| Defensive padding | No | "Inegociaveis" section is genuinely load-bearing, not restating what the LLM would do anyway |
| Meta-explanation | No | No "you are an AI assistant" framing, no explanation of why instructions exist |
| Redundant emphasis | Minimal | "never automated" appears in both SKILL.md and reference files for human gates — but this is intentional reinforcement of a safety-critical constraint, not waste |
| Over-specification | No | Agent delegations say "invoke" and "validate output", not how to construct prompts |
| Identity preamble | No | No persona construction or role-play setup |
| Hedging language | No | Instructions are direct imperatives |
| Verbose error handling | No | Error Recovery is taxonomic (3 classes, 3 responses) — concise |

**The "nunca" repetition** (appears 3 times in Inegociaveis, plus in reference files) could be flagged as emphasis stacking, but in a system where human gate bypass or empty PML delivery has real operational consequences, the reinforcement is justified. These are safety invariants, not style preferences.

---

## Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Overview quality | 9/10 | Strong framing; minor gap on script enumeration |
| Token efficiency | 10/10 | Zero waste, remarkable density for scope |
| Outcome vs implementation | 9/10 | Clean separation; delegation boundaries explicit |
| Progressive disclosure | 10/10 | Semantic phase grouping with explicit chain |
| Self-containment | 8/10 | One cross-reference to SKILL.md error handling |
| Config headers | 8/10 | Present and functional; could add dependency metadata |
| Progression conditions | 9/10 | Explicit terminal and inter-phase; minor intra-phase gap |
| Anti-patterns | 10/10 | None detected |

**Overall: 9.1/10** — This is a well-crafted orchestrator prompt. The hub-and-spoke progressive disclosure pattern is the right choice for this workflow's complexity. Token budget is exceptionally lean. The single actionable improvement is inlining the error handling cross-reference in `pre-check-and-release.md` to ensure compaction survival.

---

## Actionable Recommendations

1. **Inline error handling rule in pre-check-and-release.md** (compaction survival). Replace "report and halt per the Error Recovery section in SKILL.md" with the actual rule: "report with instructions to verify agent is installed and halt — exit 1."

2. **Consider adding script names to Overview** for completeness. A one-line list or footnote mentioning the 4 scripts (`check-verify-status.py`, `detect-task-type.py`, `check-deliverables.py`, `generate-ship-summary.py`) would give the LLM the full dependency picture at activation time.

3. **Add a micro-checkpoint between Steps 2 and 3** in the reference file (e.g., a bold "All release artifacts validated. Proceed to PML generation." line) to make intra-file progression explicit.
