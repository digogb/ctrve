# Prompt Craft Analysis — tjce-requirements
**Agent:** tjce-requirements (STATELESS — is_memory_agent: false)
**Date:** 2026-04-15
**Analyst:** PromptCraftBot

---

## Summary Verdict

This is a well-crafted, compact agent. The prompt corpus is lean (2,809 tokens across three files), structurally clean, and demonstrates deliberate design choices. Its main weaknesses are two missing `menu-code` fields in reference frontmatter and a single-capability table that adds structure without adding value. No waste patterns, no back-references, no wall-of-text — the scanner found zero pathological patterns. This agent is close to production-ready.

---

## 1. Overview Quality

**Rating: Good**

The Overview (9 lines, SKILL.md lines 9–16) does three things correctly:

- **Domain framing:** Names the institution (TJCE), the methodology (PDS Unificado), and the four mandatory artifacts. A cold-loaded model immediately knows the operational context.
- **Input contract:** States what forms of input are accepted (PRD, brief, verbal description) and how each is handled. This is outcome-first language — it tells the agent what to achieve, not how to think.
- **Flag documentation:** `--headless / -H` is documented inline in the Overview, which is the right placement for a stateless agent. The flag affects activation routing and must be visible before the agent does anything.

**What is missing:** A single sentence on the *user* — who is calling this agent and what they care about. The Overview frames the system's artifacts and the agent's mission, but never models the analyst or product manager on the other end of the conversation. For a stateless agent that must conduct interviews without prior rapport, a brief theory-of-mind anchor ("you are speaking with TJCE analysts who already know PDS Unificado terminology") would reduce unnecessary explanation in live sessions.

**Mission statement:** The Portuguese mission statement ("Garantir que todo sistema judicial...") is well-placed and well-written. It encodes the non-negotiable constraint (full traceability, no gaps) in a single sentence the agent can reactivate throughout a long context window.

---

## 2. SKILL.md Size and Progressive Disclosure

**Rating: Good**

- **62 lines / ~980 tokens** is appropriate for a single-capability skill. Well within the range where full loading on every call is acceptable.
- **Section order** follows the correct disclosure pattern: Overview → Identity → Communication Style → Principles → On Activation → Capabilities. Each section narrows scope — the agent builds a coherent self-model from broad to specific before it acts.
- **On Activation** (lines 36–55) is the pivot point: it loads config, resolves paths, determines execution mode, and gates the capability load. This is correct placement. Routing logic belongs in SKILL.md, not in the capability prompt.
- **Capabilities table** (lines 57–62): one-row table. A table with a single row is structural noise — it adds markdown parsing overhead and visual weight for no navigational benefit. At one capability, a plain sentence ("For all requests, load `references/generate-requirements.md`.") would communicate identically with fewer tokens and less ceremony. **Recommendation: replace the table with a single line.**

---

## 3. Token Efficiency

**Rating: Excellent**

The prepass found **zero waste patterns, zero back-references, zero suggestive loading, zero wall-of-text** across all three files. This is a clean bill of health.

- Total corpus: 2,809 tokens. For a 4-artifact generation workflow with interview capability and self-validation, this is genuinely efficient.
- `artifact-templates.md` at 817 tokens contains 59 lines of fenced code blocks (template markup). This is not waste — the templates are the value. They are loaded only when generation begins, not on every turn.
- `generate-requirements.md` at 1,012 tokens covers interview mode, headless mode, generation order, self-validation checklist, and output summary. No section is redundant with another.
- **One genuine efficiency question:** The Self-Validation checklist (lines 62–73 of generate-requirements.md) restates several constraints already declared in "Traceability Constraints (Non-Negotiable)" earlier in the same file. The repetition is intentional (pre-output check vs. design constraint), but two of the seven checklist items are pure duplicates of traceability constraints. Considered acceptable for a stateless agent where reinforcement at execution time reduces hallucination risk, but worth noting.

---

## 4. Outcome vs. Implementation Balance

**Rating: Good with one flag**

The agent is predominantly outcome-oriented:
- "What Success Looks Like" opens generate-requirements.md with the end state — four complete files, every cell filled, no placeholders.
- Traceability constraints are stated as invariants, not as step-by-step instructions.
- The generation order section names the *reason* each step must precede the next ("each artifact informs the next"), which is rationale, not micro-management.

**Flag:** The interview guidance (lines 33–37 of generate-requirements.md) crosses into implementation: "Extract requirements by functional area. For each area, ensure you have enough to produce all four artifacts before moving to the next." This is acceptable because interview sequencing has real downstream consequences (partial functional areas produce broken traceability). However, "Focus questions on: actors and their goals, business rules..." reads as a how-to checklist for a competent analyst who already knows what to ask. A senior analyst persona doesn't need to be told to ask about actors. **Recommendation:** Trim the focus-questions list to the non-obvious items — what to ask about exceptions and messages is genuinely domain-specific guidance; what to ask about actors and goals is generic.

---

## 5. Config Headers in Capability Prompts

**Rating: Fail — action required**

The prepass confirms: **0 of 2 reference prompts have `menu-code` in their config header.**

Both `generate-requirements.md` and `artifact-templates.md` have YAML frontmatter with `name` and `description` fields, but both are missing `menu-code`. For a single-capability agent this is a minor structural gap — there is no menu to navigate — but the `menu-code` field is part of the standard BMad reference prompt contract. Its absence means any tooling that discovers capabilities via frontmatter inspection will produce incomplete results.

**Specific finding:**
```yaml
# generate-requirements.md — missing:
menu-code: GR  # or equivalent

# artifact-templates.md — missing:
menu-code: AT  # or equivalent
```

`artifact-templates.md` is a supporting reference rather than a directly invokable capability (it has no menu entry in SKILL.md), which makes `menu-code` truly optional for it. For `generate-requirements.md`, however, the missing `menu-code` is a genuine gap.

**Recommendation:** Add `menu-code` to `generate-requirements.md` frontmatter. For `artifact-templates.md`, add a comment or a `type: reference` field to signal its non-menu nature.

---

## 6. Self-Containment (Context Compaction Survival)

**Rating: Good**

A stateless agent must be fully re-groundable from its loaded prompts alone. This agent passes the test:

- All domain terminology (PDS Unificado, US/RN/MSG ID conventions, four artifact names) is defined within the corpus.
- The path contract (`{project-root}/spec/requirements/`) is explicit.
- Config resolution logic and defaults are fully specified in On Activation.
- The headless flag behavior is described both in SKILL.md (where it affects routing) and in generate-requirements.md (where it affects assumption handling). This cross-file consistency is intentional and correct — after context compaction, whichever file is reloaded will contain the relevant branch of the logic.

**One gap:** The `[ASSUMIDO]` inline marker and `assumptions.md` output are defined only in generate-requirements.md (lines 43–44). If a long headless run compacts and reloads only SKILL.md, the agent would lose the assumption-flagging contract. This is low-risk (SKILL.md always triggers loading generate-requirements.md before generation begins) but worth noting for robustness.

---

## 7. Intelligence Placement

**Rating: Good**

Intelligence is distributed correctly across the three files:

| File | What lives here | Correct? |
|------|----------------|----------|
| SKILL.md | Identity, persona, routing, config, capability index | Yes |
| generate-requirements.md | Generation logic, traceability constraints, validation, output format | Yes |
| artifact-templates.md | Exact template markup, conventions per artifact | Yes |

The agent does not front-load all generation logic into SKILL.md (which would bloat every activation) nor does it embed routing logic into the capability prompt (which would create duplication). The separation is clean.

**One observation:** The Communication Style section in SKILL.md (lines 23–28) is persona-serving and appropriately lean. It encodes three things: language register (Portugues formal), domain vocabulary assumption (uses PDS terms without explanation), and the ambiguity-halt behavior. All three are load-bearing for a judicial analyst persona. None are waste.

---

## 8. Communication Style Consistency

**Rating: Excellent**

The corpus is bilingual by design — English for structural/meta instructions, Portuguese for domain content and persona voice. This split is deliberate and consistent throughout:

- SKILL.md structural sections (Overview, On Activation, Capabilities): English
- SKILL.md persona sections (Identity, Communication Style, Mission): Portuguese
- generate-requirements.md: English for instructions, Portuguese for artifact labels and example content
- artifact-templates.md: Portuguese throughout (as end-user-facing content)

This bilingual architecture is appropriate for a team that uses Portuguese as the operational language but English as the engineering language for prompt construction. It does not create ambiguity because the boundary is structural, not semantic.

**One inconsistency flagged:** The Principles section (SKILL.md lines 30–34) mixes languages within a single bullet: `**Rastreabilidade e completude**: Toda Regra de Negocio...` — the bold label is Portuguese but it is under a Portuguese-language section, so this is consistent. No action needed.

---

## 9. Pruning Check

**Rating: Pass — no dead instructions found**

Every instruction in the corpus maps to an observable agent behavior:

| Instruction | Behavior it produces |
|-------------|---------------------|
| `--headless` routing logic | Switches between interview and direct-generation modes |
| Config resolution (`user_name`, `output_folder`, etc.) | Personalizes output paths and communications |
| Interview termination condition ("complete when you can fill every cell") | Prevents premature generation |
| Self-validation checklist | Gates artifact output |
| `[ASSUMIDO]` marker | Enables human review of headless assumptions |
| `assumptions.md` generation | Creates a reviewable record |
| Sequential generation order | Ensures traceability links exist before referencing them |
| Artifact Formatting pointer to artifact-templates.md | Triggers lazy-load of templates at the right moment |

No instruction was found that exists for cosmetic, aspirational, or legacy reasons. The corpus has no instructions the agent cannot act on.

---

## Findings Summary

| Dimension | Rating | Action Required |
|-----------|--------|-----------------|
| Overview quality | Good | Add brief user theory-of-mind anchor |
| SKILL.md size / progressive disclosure | Good | Replace single-row table with one sentence |
| Token efficiency | Excellent | None |
| Outcome vs. implementation balance | Good | Trim generic interview focus-questions |
| Config headers in capability prompts | Fail | Add `menu-code` to generate-requirements.md |
| Self-containment | Good | Low-risk gap in assumption-flagging on compaction |
| Intelligence placement | Good | None |
| Communication style consistency | Excellent | None |
| Pruning check | Pass | None |

**Priority actions (ordered):**

1. Add `menu-code` to `references/generate-requirements.md` frontmatter. (Standards compliance.)
2. Replace the Capabilities table in SKILL.md with a single line. (Token efficiency, reduced ceremony.)
3. Add one sentence to Overview framing the human caller's context. (Theory of mind for interview mode.)
4. Trim the "Focus questions on..." list in generate-requirements.md to domain-specific items only. (Avoids patronizing a senior-persona agent.)
