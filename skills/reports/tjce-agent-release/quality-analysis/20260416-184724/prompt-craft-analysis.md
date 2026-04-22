# Prompt Craft Analysis — tjce-agent-release

**Scanner:** PromptCraftBot  
**Date:** 2026-04-16  
**Agent:** tjce-agent-release (Gerente de Release TJCE)  
**Type:** Stateless, multi-capability domain expert agent  

---

## Assessment

**Skill type:** Multi-capability domain agent (workflow facilitator + domain expert hybrid) with three capability prompts routed through a central SKILL.md. The agent generates TJCE-mandated release artifacts (PML, CHANGELOG, deploy checklist, rollback plan) from Git history and project specs.

**Overview quality:** Strong. The Overview (12 lines, ~8 sentences) establishes mission, domain context, and "what good looks like" in a compact form. The args block is well-placed and serves as operational context rather than noise. The closing "Your Mission" sentence is load-bearing — it establishes the zero-tolerance-for-empty-sections principle that drives the agent's behavior.

**Persona context quality:** Well-calibrated for a workflow facilitator. Identity (3 lines) is tight and non-redundant with Overview. Communication Style (5 bullets) is domain-specific and actionable — particularly the "zero ambiguity" and "reference obrigatoria" directives, which shape output format. Principles (4 bullets) are genuinely distinct from each other and from the sections above — each one encodes a non-obvious constraint (PML is official, rollback ALWAYS, traceability, deploy ordering).

**Progressive disclosure:** Good architecture. SKILL.md at 132 lines / ~1514 tokens is well within the 250-line guideline for multi-capability agents. Capability detail lives in `./references/` (changelog.md, deploy.md, pml.md), properly separated. Each capability prompt is self-contained with its own inputs, generation steps, headless mode, and success criteria.

**Synthesis:** This is a well-crafted domain agent. Token budget is efficient (~4613 total across all files), persona context is load-bearing throughout, and the capability prompts follow outcome-driven principles with domain-specific templates. The main areas for improvement are the absence of progression conditions in all capability prompts and a wall-of-text block in SKILL.md's headless contract section.

---

## Prompt Health Summary

| Metric | Value | Notes |
|--------|-------|-------|
| Total prompts | 3 | changelog.md, deploy.md, pml.md |
| Config headers | 3/3 | All have config note referencing parent SKILL.md variables |
| Progression conditions | 0/3 | No capability prompt defines progression gates between steps |
| Self-contained | 3/3 | All prompts include own inputs, fallback paths, and generation steps |
| Waste patterns | 0 | Clean — no defensive padding, meta-explanation, or filler detected |
| Back-references | 0 | No "as described above" or SKILL.md-dependent references |
| Suggestive loading | 0 | All references are mandatory loads |
| Walls of text | 1 | SKILL.md lines 107-130 (headless JSON block) |

---

## Per-Capability Craft

### changelog.md (96 lines, ~670 tokens)

**Outcome-driven:** Yes. "What Success Looks Like" defines 4 concrete success criteria, including negative criteria (nothing invented). Generation steps are concise and focus on what to produce, not how to think.

**Voice alignment:** Consistent with SKILL.md's checklist-oriented, reference-mandatory communication style. Steps reference US-NNN grouping and SHA traceability as established in Principles.

**Intelligence placement:** Good. Script (`extract-git-changelog.py`) handles deterministic commit extraction; prompt handles the judgment call of summarizing and grouping. Appropriate split.

**Headless mode:** Present and well-defined with clear exit code semantics (0 for success, 1 for 100% unmapped).

**Assessment:** Clean, well-scoped capability prompt. No issues found.

### deploy.md (150 lines, ~1092 tokens)

**Outcome-driven:** Yes. Success criteria are specific and actionable (numbered steps, correct ordering, rollback for every step). The template structure provides a "what good looks like" reference.

**Voice alignment:** Strong. "Rollback NUNCA e opcional" at line 139 reinforces the SKILL.md principle without being a redundant restatement — it's an in-context reminder placed exactly where the agent would be making the rollback generation decision. This is load-bearing, not waste.

**Intelligence placement:** Good. Script (`detect-deploy-changes.py`) handles deterministic file detection; prompt handles the judgment of assembling steps and adapting the checklist based on what was detected.

**Template blocks:** The two fenced code blocks (deploy checklist template at lines 36-73, rollback template at lines 75-109) are ~70 lines combined but load-bearing — they define the exact output structure for official documents. These are domain-specific templates the agent genuinely needs, not general formatting guidance.

**Assessment:** Well-crafted. The template blocks are appropriately sized for official document generation.

### pml.md (160 lines, ~1337 tokens)

**Outcome-driven:** Yes. 6 success criteria covering completeness (all 6 PML sections), traceability (every US referenced), and specificity (checks must not be generic).

**Voice alignment:** Excellent. Lines like "Nunca inventar impacto" (line 121), "Rollback NUNCA e 'nao aplicavel'" (line 145), and "Verificar se o sistema funciona e proibido" (line 149) are persona-consistent assertions that reinforce the zero-tolerance principle from SKILL.md. These are placed at decision points within the generation steps — load-bearing context, not redundancy.

**Intelligence placement:** Appropriate. The 7-step generation procedure includes judgment-heavy steps (impact analysis, validation design) alongside deterministic steps that correctly defer to scripts (metadata collection, change detection).

**Domain specificity:** The "Ordem padrao TJCE" block (lines 125-134) encodes institutional knowledge about the standard deployment sequence for the TJCE stack (FastAPI + React + PostgreSQL). This is genuinely needed domain context.

**Assessment:** The strongest capability prompt. Dense with domain knowledge, outcome-focused, and personality-consistent throughout.

---

## Key Findings

### 1. Missing Progression Conditions in All Capability Prompts

**Severity:** Medium  
**Affected files:** `references/changelog.md`, `references/deploy.md`, `references/pml.md`  
**What's wrong:** None of the 3 capability prompts define progression conditions (gates between steps). For example, pml.md's "Passo 2 — Mapear Mudancas por Estoria" should not proceed to "Passo 3 — Analisar Impacto" if zero commits were found. The agent could theoretically proceed through all 7 steps with empty data.  
**Why it matters:** Without progression gates, the agent may generate artifacts with empty sections instead of stopping early or asking for help — which directly contradicts the "nenhuma secao vazia" principle.  
**How to fix:** Add a brief progression condition after each step that specifies when to abort or ask. Example for pml.md Passo 2: "Se zero commits encontrados: stop e reportar — nao prosseguir para Analise de Impacto."

### 2. Wall of Text — Headless JSON Schema in SKILL.md

**Severity:** Low  
**Affected file:** `SKILL.md:107-130`  
**What's wrong:** The headless JSON output schema is a 24-line unstructured block (fenced code). Pre-pass flagged it as a wall of text starting at line 107.  
**Why it matters:** This is a valid template the agent needs for `--json` output, so it's not waste. However, it's the largest single block in SKILL.md and could be extracted to a reference file if SKILL.md grows.  
**How to fix:** No action needed now. If SKILL.md grows beyond 200 lines, consider extracting the JSON schema to `./references/headless-schema.json` and loading it by reference.

### 3. "Rollback ALWAYS" Principle Restated in Capability Prompts

**Severity:** Note (NOT waste)  
**Affected files:** `references/deploy.md:139`, `references/pml.md:145`  
**What's wrong:** Both deploy.md and pml.md restate the "rollback is never optional" principle from SKILL.md:36.  
**Why it matters:** This is NOT redundancy — it is self-containment. If context compaction drops SKILL.md, these in-prompt reminders ensure the agent still generates rollback plans. The placement is also strategic: each restatement appears inside the rollback generation step, exactly where the agent needs the reminder. This is a strength, not a finding.

---

## Strengths

- **Token efficiency is excellent.** Total budget of ~4613 tokens across 4 files for a 3-capability domain agent with full templates is lean. No waste patterns, no defensive padding, no back-references detected.

- **Self-containment is fully achieved.** Every capability prompt includes its own inputs section, fallback paths, generation steps, success criteria, and headless mode. None depend on SKILL.md being in context. The config note at the top of each prompt explains variable resolution without being verbose.

- **Persona is consistent and load-bearing.** The "zero ambiguity, zero placeholders, rollback always" personality is established in SKILL.md and naturally expressed throughout capability prompts without mechanical repetition. The voice is appropriately formal for official judicial documents.

- **Intelligence placement is correct throughout.** Three scripts handle deterministic operations (git log extraction, deploy change detection, artifact validation) while prompts handle judgment calls (summarization, impact analysis, checklist assembly, validation design).

- **Domain templates are appropriately detailed.** The PML, CHANGELOG, and deploy checklist templates provide "what good looks like" exemplars that encode TJCE-specific institutional knowledge (document structure, required fields, standard deploy ordering). These are genuine domain context, not LLM hand-holding.

- **Headless mode is well-specified.** SKILL.md defines exit codes, arg resolution order, and fallback strategies. Each capability prompt adds its own headless behavior. The JSON output schema provides a complete contract for automation consumers.

- **Capability routing table is clean.** Three capabilities, three codes (P/C/D), clear routing. The sequential execution order for `--task-type all` (PML -> CHANGELOG -> DEPLOY) is specified.
