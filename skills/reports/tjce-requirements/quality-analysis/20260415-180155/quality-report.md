# BMad Method · Quality Analysis: tjce-requirements

**Analista de Requisitos TJCE** — Analista de Requisitos do TJCE para PDS Unificado
**Analyzed:** 2026-04-15T18:01:55Z | **Path:** skills/tjce-requirements/
**Interactive report:** quality-report.html

## Agent Portrait

The Analista de Requisitos TJCE is a methodical, precision-driven judicial requirements analyst who refuses to tolerate ambiguity. Speaking in formal Portuguese with the vocabulary of Brazilian court systems, this agent stops mid-flow to interrogate vague requirements rather than fill gaps with assumptions. It produces the four mandatory PDS Unificado artifacts — Product Vision, User Stories, Business Rules, and System Messages — with ironclad traceability: every rule traces to a story, every message traces to a rule, and no cell is left to "TODO."

## Capabilities

| Capability | Status | Observations |
| ---------- | ------ | ------------ |
| Gerar Especificacao de Requisitos | Needs attention | 4 findings across scanners |

## Assessment

**Good** — This agent demonstrates strong domain design with a rigorous traceability model and clean prompt architecture (2,809 tokens, zero waste patterns). Its primary opportunity is hardening the lifecycle beyond initial generation: adding progression markers to capability files, building context management for large systems, and extracting deterministic validation work into scripts.

## Opportunities

### 1. Missing Progression and Flow Control Markers (high — 3 observations)

The capability file `generate-requirements.md` contains meaningful procedural logic — two execution branches, a four-step sequential generation order, and a self-validation gate — but expresses all of this through natural language structure rather than explicit conditional keywords. The template file `artifact-templates.md` was also flagged but is a false positive (static reference, not a capability). Without explicit markers, automated tooling cannot parse the flow, and future maintainers may miss branching logic.

**Impact:** Improves parsability for tooling, reduces maintainer confusion, and makes the generation flow explicit and auditable.

**Action:** Add explicit progression markers to `generate-requirements.md` at three decision points: (1) "If interview mode..." / "If PRD mode..." at the branch, (2) "Proceed to [next artifact] only when [current artifact] is complete" at generation steps, (3) "Do not output artifacts until all checklist items pass" at the validation gate. No changes needed for `artifact-templates.md`.

- `generate-requirements.md:83` — No progression condition keywords found (structure-capabilities-prepass)
- `artifact-templates.md:117` — No progression keywords; assessed as false positive for template file (structure-capabilities-prepass)
- `generate-requirements.md` — Progression expressed through section headers rather than explicit conditional keywords (structure-analysis)

### 2. Context Pressure and Session Resilience Gaps (medium — 5 observations)

Multiple scanners identified that the agent has no strategy for managing context growth in large systems or recovering from interrupted sessions. For systems with 50+ user stories and 100+ business rules, artifact tables can consume significant context. Interview transcripts are carried verbatim through all four generation phases. There is no checkpointing, no partial output recovery, and no interview summarization step.

**Impact:** Fixing this theme would prevent degraded output quality for large systems, enable session resumption for multi-day requirements gathering, and reduce context waste during generation.

**Action:** Add three mechanisms to `generate-requirements.md`: (1) a transition step between interview completion and generation that synthesizes the dialogue into a compact requirements brief, (2) a guidance note to write each artifact to disk immediately and reference the file for cross-artifact checks rather than relying on in-context copies, (3) an activation check in SKILL.md to scan for existing partial output and offer resume behavior.

- `generate-requirements.md` — No context pressure guard for large systems (execution-efficiency)
- `generate-requirements.md` — Interview transcript not summarized before generation (execution-efficiency)
- `SKILL.md` — No partial output recovery on session restart (execution-efficiency)
- `generate-requirements.md` — No re-entry path after partial session (enhancement-opportunities)
- `generate-requirements.md` — Validation failure with no rollback; artifacts may be left in inconsistent state (enhancement-opportunities)

### 3. Lifecycle Gaps: No Update or Review Capabilities (medium — 4 observations)

The agent excels at creating requirements from scratch but has no flow for updating existing artifacts, validating third-party artifacts, or handling iterative review cycles. Real projects evolve: new stories enter, rules change, and stakeholders request revisions. Without these flows, the agent is discarded after initial generation or requires manual rework outside its control.

**Impact:** Adding incremental update and review capabilities would extend the agent's usefulness across the full project lifecycle, not just the initial specification phase.

**Action:** Add two new capabilities: (1) an update mode that detects existing artifacts and presents changes as diffs before applying, (2) a validation-only mode that audits existing artifacts for traceability and completeness without regenerating. Reference these in the Capabilities table.

- Agent has no flow for updating already-generated artifacts (agent-cohesion)
- No capability for autonomous validation of existing artifacts (agent-cohesion)
- No diff view for iterative sessions (enhancement-opportunities)
- Missing "review mode" in three-mode architecture (enhancement-opportunities)

### 4. Deterministic Validation Delegated to LLM (medium — 6 observations)

Eleven deterministic operations — ID sequence validation, cross-reference integrity checks, placeholder detection, message type coverage, and traceability counting — are currently performed by the LLM at an estimated cost of 2,250-3,200 tokens per invocation. These are pure string/set operations that could be handled by scripts with zero token cost and guaranteed correctness.

**Impact:** Extracting these to scripts eliminates ~2,500 tokens of LLM tax per run, improves validation reliability, and enables CI integration.

**Action:** Create a `scripts/` directory with post-processing validators: `validate-ids.py` (SO-003), `check-rn-us-refs.py` (SO-004), `check-msg-rn-refs.py` (SO-005), `detect-placeholders.py` (SO-007). Start with the three P0 cross-reference scripts (~1,050 tokens saved, implementable in under an hour).

- Self-validation checklist delegates ID validation to LLM (script-opportunities)
- Cross-reference RN to US check delegated to LLM (script-opportunities)
- Cross-reference MSG to RN check delegated to LLM (script-opportunities)
- Placeholder/empty cell detection delegated to LLM (script-opportunities)
- Message type coverage check delegated to LLM (script-opportunities)
- Assumptions file compilation delegated to LLM (script-opportunities)

### 5. Missing Soft Gates and User Experience Polish (medium — 5 observations)

The agent lacks soft gates at critical transition points: no scope confirmation before generation, no coverage map after reading a PRD, no onboarding preamble for first-timers, and no graceful handling of "I don't know" answers during interviews. These gaps create friction for all user archetypes.

**Impact:** Adding soft gates and experience polish would reduce mid-generation rework, improve first-timer onboarding, and prevent scope misunderstandings.

**Action:** Add three mechanisms: (1) a pre-generation scope confirmation ("Entendi que este sistema faz X para atores Y. Confirma?"), (2) a coverage map after loading a PRD showing which areas are complete vs. incomplete, (3) a deferred item queue for "nao sei" answers during interviews that collects unknowns and presents them as a focused mini-questionnaire before generation.

- No soft gate elicitation before generation (enhancement-opportunities)
- No intent-before-ingestion pattern when reading documents (enhancement-opportunities)
- No "I don't know" recovery path during interviews (enhancement-opportunities)
- No onboarding preamble for first-timers (enhancement-opportunities)
- No scope creep warning during interview (enhancement-opportunities)

## Strengths

- **Rigorous traceability model**: The bidirectional traceability chain (US to RN to MSG) with self-validation is a genuine domain design strength, not just template work. The generation order enforces dependency correctness.
- **Zero-waste prompt architecture**: 2,809 tokens across three files with zero waste patterns, zero back-references, zero wall-of-text, and zero suggestive loading. Every instruction maps to an observable behavior.
- **Strong persona-capability alignment**: The identity ("metodico, preciso, desconfortavel com ambiguidade") directly drives behavioral rules — the no-placeholder prohibition, the stop-and-ask stance, and the self-validation gate all flow from the declared persona.
- **Clean intelligence placement**: SKILL.md handles identity and routing, generate-requirements.md handles execution logic, artifact-templates.md handles format. No cross-contamination between layers.
- **Well-specified headless mode**: Entry condition, input resolution, fallback error behavior, mid-generation ambiguity handling via [ASSUMIDO], and audit trail via assumptions.md — the headless path is complete.
- **Bilingual architecture done right**: English for structural/meta instructions, Portuguese for domain content and persona voice, with consistent boundaries throughout.
- **Correct delegation of procedural detail**: SKILL.md avoids over-specification by delegating all interview flow, generation order, and validation checklists to reference files.

## Detailed Analysis

### Structure & Capabilities

The agent has all six required SKILL.md sections in correct order. The single-capability routing table is valid — both referenced files exist. The frontmatter description has strong routing triggers but the name field lacks the "agent" convention (`tjce-requirements` instead of `tjce-agent-requirements`). One low-severity observation: the description omits "product vision" as a trigger phrase despite it being a mandatory output. The output path in `generate-requirements.md` (`spec/requirements/`) is hardcoded and bypasses the configurable `{output_folder}` variable, creating a potential configuration inconsistency.

- `SKILL.md:1` — Name "tjce-requirements" should contain "agent" (medium, structure-capabilities-prepass)
- `SKILL.md` — Description missing "product vision" as trigger phrase (low, structure-analysis)
- `generate-requirements.md:12` — Hardcoded output path bypasses configurable {output_folder} (low, structure-analysis/agent-cohesion)

### Persona & Voice

The agent's prompt craft is strong. The Overview is outcome-first, the Identity is behaviorally grounded, and the Communication Style rules are terse and LLM-actionable. Token efficiency is excellent at 2,809 tokens total with zero pathological patterns detected. The single-row Capabilities table adds structural noise that could be replaced with a single sentence. Both reference prompts are missing `menu-code` in their frontmatter. One minor gap: the Overview does not model the human caller (theory-of-mind anchor), which would improve interview interactions.

- `references/generate-requirements.md:1` — Missing menu-code in frontmatter (medium, prompt-craft)
- `references/artifact-templates.md:1` — Missing menu-code in frontmatter (low, prompt-craft — template file, optional)
- `SKILL.md` — Capabilities table with single row adds unnecessary ceremony (low, prompt-craft)
- `SKILL.md` — Overview missing theory-of-mind anchor for human caller (low, prompt-craft)

### Identity Cohesion

Persona-capability alignment is strong — the identity traits (methodical, precise, ambiguity-averse) directly manifest in behavioral rules across all files. The traceability constraints in Principles mirror the Non-Negotiable constraints in generate-requirements.md identically. One intentional redundancy exists (traceability constraints stated in both SKILL.md and generate-requirements.md) but is structurally justified and must be kept synchronized. The agent lacks flows for post-delivery lifecycle stages (updates, reviews, iteration) and has no protocol for conflicting input documents.

### Execution Efficiency

The automated dependency prepass found zero issues, which is expected for a conversational orchestrator. Manual analysis identified that reference files are loaded lazily when they could be loaded eagerly at activation in parallel with config. The sequential artifact generation order is a correctness requirement (dependency chain), not an efficiency gap. The self-validation checklist could be reframed as a single-pass audit rather than seven sequential checks.

### Conversation Experience

Six user archetypes were stress-tested. The most critical gaps are the absence of a soft gate before generation (the agent can race into artifact creation with insufficient information) and no "I don't know" recovery path during interviews. First-timers receive no onboarding explanation of the four PDS Unificado artifacts. Experts cannot skip or customize the interview flow. Automators lack exit codes, machine-readable quality signals, and a dry-run mode.

**User Journeys:**

- **First-timer**: Struggles with no explanation of what the four artifacts are, no upfront interview length estimate, and no guidance on exception detail level. The experience is functional but opaque.
- **Expert**: Cannot skip interview when providing a verbal brief, cannot customize artifact depth, and has no batch mode for multiple systems. Functional but slow for repeat users.
- **Confused user**: A developer running the tool without domain knowledge will enter an interview they cannot answer. No "wrong person" detection exists.
- **Edge-case (minimal system)**: The four-message-type constraint may force artificial confirmations for read-only systems. The constraint needs a documented exception path.
- **Hostile environment**: Auto-generated PRDs with mixed languages, duplicate sections, or inconsistent terminology receive no normalization. The agent may produce conflicting rules from duplicate input sections.
- **Automator**: No exit codes, no machine-readable output summary, no dry-run mode, and no stable schema for assumptions.md. Headless mode is functional but underbuilt for CI/CD integration.

**Autonomous/Headless Potential:** Partially adaptable. Headless mode exists and handles assumptions, but lacks quality scoring, confidence gradients, exit code semantics, and input validation. Significant enhancements needed for true CI/CD integration.

### Script Opportunities

Eleven deterministic operations were identified as script candidates, representing an estimated 2,250-3,200 tokens of LLM tax per invocation. The highest-value extractions are the three cross-reference integrity checks (SO-003, SO-004, SO-005) at ~1,050 tokens combined, implementable in under an hour. Pre-processing scripts for config loading and input scanning would also reduce activation overhead. A recommended `scripts/` directory structure with pre/ and post/ subdirectories was proposed.

## Recommendations

1. **Add progression markers to generate-requirements.md** — Resolves 3 findings across structure prepass and structure analysis. Add explicit if/proceed/complete keywords at the three decision points. (effort: low)
2. **Build context management for large systems** — Resolves 5 findings. Add interview summarization, write-to-disk-first guidance, and partial output recovery. (effort: medium)
3. **Extract top-3 validation scripts** — Resolves 3 findings. Create validate-ids.py, check-rn-us-refs.py, and check-msg-rn-refs.py as post-processing scripts. Saves ~1,050 tokens/run. (effort: low)
4. **Add soft gates and experience polish** — Resolves 5 findings. Pre-generation scope confirmation, coverage map, deferred item queue for unknowns. (effort: medium)
5. **Add incremental update capability** — Resolves 4 findings. Detect existing artifacts, offer diff mode, add review-only capability. (effort: high)
6. **Add menu-code to generate-requirements.md frontmatter** — Resolves 1 finding. Standards compliance fix. (effort: low)
7. **Fix output path configuration inconsistency** — Resolves 2 findings. Replace hardcoded `spec/requirements/` with `{output_folder}/requirements/`. (effort: low)
8. **Rename skill to include "agent" in name** — Resolves 1 finding. Rename to `tjce-agent-requirements` and update directory references. (effort: low)
