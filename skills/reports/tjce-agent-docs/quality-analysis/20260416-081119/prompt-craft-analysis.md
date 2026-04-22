# Prompt Craft Analysis — tjce-agent-docs

## Assessment

**Skill type:** Single-capability stateless agent (domain expert / technical writer).

**Overview quality:** Strong. The Overview (9 lines, ~1330 tokens total SKILL.md) establishes mission, audience, domain framing, and theory of mind in a concise package. The mission statement in Portuguese ("Nenhum usuario do tribunal precisa pedir ajuda...") is evocative and outcome-focused — it tells the agent what "good" looks like, not just what to do. Domain vocabulary (US, tela, mensagens, servidor, magistrado) is introduced naturally.

**Persona context quality:** Well-crafted. Identity (line 18-20) and Communication Style (line 22-28) are distinct sections with no redundancy between them. Identity establishes the voice ("escreve como quem explica para um colega leigo"), Communication Style gives concrete rules (imperative mood, visible labels, quoted messages). Principles (line 30-35) add behavioral guardrails that are genuinely load-bearing (traceability, never-invent-screens). This is investment, not waste.

**Progressive disclosure:** Correct architecture. SKILL.md is 97 lines (~1330 tokens) — well within the 250-line guideline for a multi-section single-capability agent. The one capability prompt lives in `references/manual-capability.md` (153 lines, ~1681 tokens). Total token budget of ~3011 is lean and efficient.

**Synthesis:** This is a well-crafted agent prompt. The persona context is load-bearing and proportionate to the agent's domain (judicial user documentation requires careful tone calibration). The capability prompt is outcome-driven with appropriate procedural detail for a document-generation task. No waste patterns, no back-references, no wall-of-text blocks were detected by the pre-pass, and manual review confirms this. The few findings below are minor refinements, not structural issues.

## Prompt Health Summary

| Metric | Value |
|--------|-------|
| Total prompts | 1 |
| Config headers present | 1/1 |
| Progression conditions | 0/1 |
| Self-contained | 1/1 |
| Waste patterns detected | 0 |
| Back-references detected | 0 |

## Per-Capability Craft

### references/manual-capability.md (Code: M)

**Outcome focus:** Good. "What Success Looks Like" (line 13-19) defines 5 clear success criteria that are measurable and outcome-oriented. The capability prompt opens with what it produces and for whom — not how.

**Voice consistency:** Consistent with SKILL.md persona. Portuguese institutional tone maintained throughout. Prohibited terms list and substitution table reinforce the agent's zero-jargon identity.

**Procedural balance:** The 6-step generation process (lines 79-138) is appropriate for this task. Document generation from multiple input sources is genuinely complex — the steps guide the agent through inventory, mapping, drafting, and validation in a way that prevents common failure modes (inventing screens, missing messages). This is not over-specification; it is domain-specific workflow that the agent cannot derive from persona alone.

**Self-containment:** The config note at line 7 clarifies variable resolution without back-referencing SKILL.md content. The prompt restates key behavioral rules (imperative voice, visible labels, prohibited terms) that also appear in SKILL.md — this is correct for context compaction survival, not redundant waste.

## Key Findings

### 1. Missing progression conditions in capability prompt

- **Severity:** Medium
- **File:** `references/manual-capability.md`
- **What:** The capability prompt has no explicit progression gates between steps. Pre-pass confirms `has_progression: false`.
- **Why it matters:** In headless mode, the agent could skip validation (Passo 5) if context compacts mid-generation. In interactive mode, the agent could proceed past Passo 2 without confirming screen mapping completeness.
- **Fix:** Add brief progression conditions between critical steps. At minimum, after Passo 1 ("Proceed only when US inventory is complete") and after Passo 5 ("Proceed to write only when all checks pass or gaps are explicitly marked").

### 2. Substitution table could be a reference file

- **Severity:** Low
- **File:** `references/manual-capability.md:114-123`
- **What:** The prohibited-terms list and substitution table (lines 110-123) are inline in the capability prompt. Currently small (7 rows) but likely to grow as more TJCE systems are documented.
- **Why it matters:** If the table grows beyond ~15 entries, it will consume capability prompt tokens that could be better spent on judgment context. Currently acceptable.
- **Fix:** No action needed now. If the table grows, extract to `references/terminology-map.md` and load explicitly.

### 3. Screen Pre-Pass script reference assumes Python availability

- **Severity:** Low
- **File:** `SKILL.md:58-60`
- **What:** The pre-pass calls `python3 scripts/extract-screens.py` without checking if Python is available or if the script exists. The section is labeled "optional" but has no graceful fallback instruction.
- **Why it matters:** If the script is missing or Python unavailable, the agent may error or stall. The capability prompt (Passo 2, line 91) already handles the fallback case well — but SKILL.md does not connect the two.
- **Fix:** Add a one-line note: "If script unavailable, skip — capability prompt handles fallback."

## Strengths

- **Mission statement is exemplary.** The Portuguese mission ("Nenhum usuario do tribunal precisa pedir ajuda...") is one of the best patterns for agent prompts — it defines what good looks like in a single sentence that the agent can use as a decision framework for edge cases.
- **Zero waste detected.** No defensive padding, no meta-explanation, no back-references. Every section carries its weight. The pre-pass confirmed zero waste patterns, and manual review agrees.
- **Persona-capability separation is clean.** SKILL.md owns identity, voice, and principles. The capability prompt owns workflow and domain rules. No bleeding between the two — and where behavioral rules are restated in the capability prompt (prohibited terms, imperative voice), it is correctly done for self-containment.
- **Headless contract is well-specified.** Exit codes, structured JSON output, and graceful degradation (marking incomplete sections rather than inventing) show mature agent design.
- **"Never invent" principle is load-bearing.** For a documentation agent, this is the single most important guardrail. It is established in Principles (line 34) and reinforced in the capability prompt (lines 19, 91, 132, 144). This repetition is correct — it is the agent's most critical behavioral constraint.
- **Substitution table is practical.** Rather than just saying "no jargon," the prompt gives concrete mappings. This is exactly the kind of domain knowledge an LLM needs to produce correct output.
