# Structure Analysis — tjce-requirements

**Scanner:** StructureBot  
**Agent Path:** `skills/tjce-requirements/`  
**Memory Agent:** false (stateless)  
**Date:** 2026-04-15  
**Pre-pass Status:** warning (5 issues: 0 critical, 2 high, 3 medium, 0 low)

---

## 1. Frontmatter Quality

**File:** `SKILL.md`

```yaml
name: tjce-requirements
description: Analista de Requisitos do TJCE para PDS Unificado. Use when the user asks to generate requirements, create user stories, business rules, or system messages for TJCE projects.
```

### `name`

**Status: FAIL (medium)**

The name `tjce-requirements` follows a `{code}-{function}` pattern rather than the required `{code}-agent-{name}` or `agent-{name}` convention. The word "agent" is absent from the name field.

**Recommendation:** Rename to `tjce-agent-requirements` or `agent-tjce-requirements` depending on the project's naming scheme. The directory name and any internal cross-references would need to be updated in sync.

### `description`

**Status: PASS**

The description meets the two-part convention: the first sentence provides a human-readable label ("Analista de Requisitos do TJCE para PDS Unificado") and the second sentence provides routing guidance starting with "Use when..." and lists concrete trigger phrases (generate requirements, create user stories, business rules, system messages for TJCE projects). The trigger phrases are specific and actionable; a dispatcher model can reliably route to this agent.

---

## 2. Required Sections

All six required sections are present and in the correct order. Line references are from the pre-pass scan.

| Section | Line | Status |
|---|---|---|
| Overview | 8 | PASS |
| Identity | 18 | PASS |
| Communication Style | 22 | PASS |
| Principles | 30 | PASS |
| On Activation | 36 | PASS |
| Capabilities | 57 | PASS |

**Section coverage: 6/6 — PASS**

The pre-pass also detected a `### Input Detection` subsection (line 46) nested under `On Activation`. This is a structural addition, not a violation; it meaningfully decomposes activation logic into four clearly labeled branches and is acceptable.

---

## 3. Description Quality

**Status: PASS**

Trigger phrases are concrete and cover the primary demand surface for this agent:

- "generate requirements"
- "create user stories"
- "business rules"
- "system messages for TJCE projects"

The TJCE scoping qualifier ("for TJCE projects") prevents the agent from being incorrectly activated for generic requirements work outside this domain. Specificity is adequate.

**Minor observation (low severity):** The description does not mention "Product Vision" as a trigger phrase, even though generating `product-vision.md` is listed as a mandatory output in `generate-requirements.md`. A user asking "create a product vision for a TJCE system" may not be routed here by a dispatcher. Adding "product vision" to the trigger list would close this gap.

---

## 4. Identity Effectiveness

**File:** `SKILL.md`, lines 19–20

> Analista de requisitos senior com experiencia em sistemas judiciais — metodico, preciso, e desconfortavel com ambiguidade. Quando encontra algo vago, para e pergunta antes de assumir.

**Status: PASS**

The identity is tight and behaviorally grounded. Three traits are established ("metodico, preciso, e desconfortavel com ambiguidade") and the closing sentence encodes a concrete behavioral rule ("para e pergunta antes de assumir") that directly shapes output quality. The identity is in Portuguese, consistent with the agent's operating language. It does not over-describe the persona or introduce contradictions with any other section.

---

## 5. Communication Style Quality

**File:** `SKILL.md`, lines 23–28

**Status: PASS**

Five rules are defined. Each rule is actionable and non-redundant:

1. Language and register: formal Portuguese, judicial vocabulary.
2. Verbosity: direct, no filler.
3. Terminology: use PDS Unificado terms without explaining them (assumes a trained audience).
4. Ambiguity handling: interrupt flow, identify the exact point, ask the specific question.
5. Prohibition: never use placeholders ("TODO", "a definir", "verificar posteriormente").

Rules 4 and 5 reinforce each other and align with the Identity's "never assume" stance. No contradictions. The style rules are terse and LLM-actionable.

---

## 6. Principles Quality

**File:** `SKILL.md`, lines 32–34

**Status: PASS**

Three principles are defined as bold-labeled rules:

1. **Rastreabilidade e completude** — encodes the hard traceability constraints (RN→US, MSG→RN, RN→test case). These mirror exactly the "Non-Negotiable" constraints in `generate-requirements.md`, creating structural consistency between SKILL.md and the referenced capability file.
2. **Ambiguidade e zero** — reinforces the identity's "stop and ask" stance with an explicit prohibition on assumptions and placeholders.
3. **Consistencia entre projetos** — mandates template fidelity across all TJCE systems.

All three principles are verifiable (each can be evaluated post-generation by inspection). No over-broad philosophical statements. Depth is appropriate for a stateless agent.

---

## 7. Logical Consistency

**Status: PASS with one observation**

Cross-file consistency check across `SKILL.md`, `generate-requirements.md`, and `artifact-templates.md`:

- The traceability constraints in `Principles` (SKILL.md line 32) are identically reproduced as "Non-Negotiable" constraints in `generate-requirements.md` lines 23–29. No divergence.
- The four artifacts listed in `generate-requirements.md` ("What Success Looks Like", lines 14–17) match the four templates defined in `artifact-templates.md` exactly.
- The self-validation checklist in `generate-requirements.md` (lines 65–71) is consistent with both the principles and the template conventions in `artifact-templates.md`.
- The `[ASSUMIDO]` flag behavior in `generate-requirements.md` (line 43) is consistent with the headless mode branch in `On Activation` (SKILL.md line 51).
- The generation order (Vision → Stories → Rules → Messages) is logically sound: each artifact's constraints depend on the prior one being complete.

**Observation (low severity):** `generate-requirements.md` (line 12) specifies a hardcoded output path of `{project-root}/spec/requirements/`. The `On Activation` section defines `{output_folder}` (default: `{project-root}/_bmad-output`) as a configurable variable. The output path in the capability file bypasses this variable entirely. If a user overrides `{output_folder}` in their config, the generated files will still land at `spec/requirements/` rather than under the configured output folder. The two paths are architecturally inconsistent. Recommend replacing the hardcoded path with `{output_folder}/requirements/` or documenting `spec/requirements/` as an intentional fixed convention independent of the output config.

---

## 8. Headless Mode Setup

**Status: PASS**

Headless mode is documented at three levels, forming a complete specification:

1. **Overview** (SKILL.md line 14): Declares the `--headless` / `-H` flag and its precondition (requires PRD or brief as input).
2. **Input Detection** (SKILL.md lines 50–51): Branch 1 specifies exactly what happens under the flag — scan for structured input at `{planning_artifacts}` or from a path argument, proceed to generation if found, or exit with an error that explains what input is required.
3. **generate-requirements.md** (lines 42–44): The `[ASSUMIDO]` flag mechanism is the headless-mode equivalent of the interactive "stop and ask" rule, ensuring ambiguity handling is defined for both modes. The `assumptions.md` output file ensures headless runs remain auditable.

The headless path covers: entry condition, input resolution, fallback error behavior, mid-generation ambiguity handling, and audit trail. No gaps.

---

## 9. Capability Routing

**File:** `SKILL.md`, lines 57–62

```
| Capability                        | Route                                       |
| --------------------------------- | ------------------------------------------- |
| Gerar Especificacao de Requisitos  | Load `references/generate-requirements.md` |
```

**Route target:** `skills/tjce-requirements/references/generate-requirements.md`

**File existence:** CONFIRMED — file exists at the expected path.

**Secondary route:** `generate-requirements.md` (line 57) instructs: "Load `./artifact-templates.md` for the exact markdown structure of each artifact." This resolves to `skills/tjce-requirements/references/artifact-templates.md`.

**File existence:** CONFIRMED — file exists at the expected path.

**Routing status: PASS** — both referenced files exist and are loadable.

**Note:** The Capabilities table contains a single capability. This is appropriate for an agent with a focused, well-scoped function. No missing capability entries are identified relative to what the agent advertises in its description or Overview.

---

## 10. Over-specification Check

**Status: PASS**

This agent avoids over-specification in the SKILL.md layer. The SKILL.md correctly delegates all procedural detail (interview flow, generation order, validation checklists, template structure) to the reference files. The main skill file provides identity, behavior guardrails, activation logic, and routing — which is the correct division of responsibility.

`generate-requirements.md` is substantive but not over-specified: it defines constraints, order of operations, and validation rules without scripting exact LLM dialogue or hard-coding domain-specific content that belongs in the templates. `artifact-templates.md` is appropriately minimal — it contains structure and conventions only, not logic.

---

## 11. Pre-pass Issues — Structural Assessment

The pre-pass flagged 5 issues. This section evaluates each from a structural perspective.

### Issue 1: Name missing "agent" (medium) — CONFIRMED

**File:** `SKILL.md`, line 1  
**Assessment:** Valid violation. The name field does not follow the `agent-{name}` or `{code}-agent-{name}` convention. See Section 1 above.  
**Impact:** May affect agent discovery or orchestration systems that rely on the naming convention to identify agents.

### Issue 2: No config header in `artifact-templates.md` (medium) — CONTEXTUALLY ACCEPTABLE

**File:** `artifact-templates.md`, line 1  
**Assessment:** `artifact-templates.md` is a pure template reference file — it contains no procedural logic, no branching behavior, and no user-facing communication. It exists solely to define markdown structure. A config header with language variables would be appropriate if the templates contained text that needed to be rendered in a language specified at runtime. However, all template placeholder text is already in Portuguese (e.g., `{Descricao do que o sistema faz}`, `{perfil/ator}`) and the file's purpose is format enforcement, not content generation.

A config header would add no functional value here and could create confusion about whether the template text itself is configurable. The absence is acceptable given the file's role.

**Recommendation:** If the project intends to support multilingual template headers in the future, add a minimal config block. For current scope, no action required.

### Issue 3: No progression condition keywords in `artifact-templates.md` (high) — FALSE POSITIVE FOR THIS FILE TYPE

**File:** `artifact-templates.md`, line 117  
**Assessment:** Progression condition keywords (e.g., "if", "when", "unless", "proceed", "complete") are relevant in capability files that define procedural flows with decision points. `artifact-templates.md` is not a capability file — it is a static reference document containing markdown templates. There is no flow to progress through; the file is loaded and read, not executed.

Flagging a template library for missing progression conditions is a category error by the scanner. The issue does not represent a real structural deficiency.

**Recommendation:** The pre-pass script should exclude files whose `description` frontmatter indicates a template or reference role from the progression-condition check.

### Issue 4: No config header in `generate-requirements.md` (medium) — PARTIALLY VALID

**File:** `generate-requirements.md`, line 1  
**Assessment:** Unlike `artifact-templates.md`, `generate-requirements.md` is a capability file that drives active LLM behavior. It references config variables (`{project-root}`, `{planning_artifacts}`) inherited from the SKILL.md's `On Activation` section, but does not declare its own config header.

The current design — where config is loaded once in `On Activation` and variables flow through to all loaded reference files — is a valid pattern for stateless agents. A local config header in the capability file would only be needed if the file were designed to be invoked independently outside of the SKILL.md context.

**Assessment verdict:** The absence is intentional by design (config inheritance from SKILL.md). However, the file would benefit from a comment or note clarifying that it relies on variables resolved during activation, to prevent future maintainers from treating it as a standalone prompt.

**Recommendation:** Add a brief note at the top of `generate-requirements.md` (below the frontmatter) stating that config variables (`{project-root}`, `{planning_artifacts}`, `{output_folder}`, `{communication_language}`) are resolved by the parent SKILL.md at activation time.

### Issue 5: No progression condition keywords in `generate-requirements.md` (high) — PARTIALLY VALID

**File:** `generate-requirements.md`, line 83  
**Assessment:** `generate-requirements.md` is a capability file with meaningful procedural flow: it defines two execution branches (interview vs. PRD-based generation), a generation order with four sequential steps, and a self-validation gate before output. However, the progression is expressed through section headers and bullet structure rather than explicit conditional keywords.

The behavior IS conditional and sequential — it just uses natural language structure rather than explicit markers like "if", "proceed when", or "complete when". This is not a functional deficiency but it does reduce the file's parsability for automated tooling and future maintainers.

**Recommendation:** Add explicit progression markers at key decision points:
- At the interview/PRD branch: "If interview mode..." / "If PRD mode..."
- At the generation order: "Proceed to [next artifact] only when [current artifact] is complete."
- At the self-validation gate: "Do not output artifacts until all checklist items pass."

---

## 12. Summary

| Check | Status |
|---|---|
| Frontmatter — name convention | FAIL (medium) |
| Frontmatter — description quality | PASS |
| Required sections (6/6) | PASS |
| Description trigger phrases | PASS |
| Description — product vision gap | observation (low) |
| Identity effectiveness | PASS |
| Communication style | PASS |
| Principles quality | PASS |
| Logical consistency | PASS |
| Output path inconsistency | observation (low) |
| Headless mode specification | PASS |
| Capability routing — file existence | PASS |
| Over-specification | PASS |
| Pre-pass: name missing "agent" | CONFIRMED |
| Pre-pass: no config header (artifact-templates.md) | CONTEXTUALLY ACCEPTABLE |
| Pre-pass: no progression (artifact-templates.md) | FALSE POSITIVE |
| Pre-pass: no config header (generate-requirements.md) | PARTIALLY VALID |
| Pre-pass: no progression (generate-requirements.md) | PARTIALLY VALID |

### Issues Requiring Action

| Priority | Issue | File | Recommendation |
|---|---|---|---|
| Medium | Name missing "agent" | SKILL.md | Rename to `tjce-agent-requirements` |
| Low | Output path not using config variable | generate-requirements.md | Replace `spec/requirements/` with `{output_folder}/requirements/` |
| Low | Progression markers absent | generate-requirements.md | Add explicit if/proceed/complete markers at decision points |
| Low | No clarity note on config inheritance | generate-requirements.md | Add comment that variables are resolved by parent SKILL.md |
| Low | "product vision" missing from trigger phrases | SKILL.md description | Add "product vision" to the description's trigger phrase list |

### Issues Not Requiring Action

| Pre-pass Issue | Reason |
|---|---|
| No config header in artifact-templates.md | Template-only file; no procedural logic to configure |
| No progression in artifact-templates.md | Not a capability file; scanner category error |
