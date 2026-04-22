# Prompt Craft Analysis — tjce-agent-apf

## Assessment

**Skill type:** Stateless domain-expert agent (single-capability). IFPUG Function Point analyst targeted at TJCE judicial systems. The agent is deterministic-leaning (scripts do arithmetic/classification) with judgment layered over domain interpretation (what is an ALI vs AIE, DER counting, orphan detection).

**Overview quality:** Strong. SKILL.md Overview (lines 8-14) combines mission, interlocutor theory-of-mind ("gestor de metricas do TJCE ou desenvolvedor"), domain framing (ALI/AIE/EE/SE/CE, fast-path Garantia), args documentation, and a crisp mission statement. Does not exceed size guidelines (7 Overview lines, 1261 tokens total in SKILL.md).

**Persona context quality:** Well-balanced. Identity (4 lines), Communication Style (5 bullets with concrete examples like "ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF"), and Principles (4 load-bearing rules: Determinismo IFPUG, Rastreabilidade, Nao contar em dobro, Pergunte nao assuma). Each principle maps to observable agent behavior — not philosophical filler.

**Progressive disclosure:** Correct. SKILL.md = 74 lines / 1261 tokens; capability detail (205 lines / 2011 tokens) lives in `references/count-capability.md` and is loaded on routing. Single capability with a clear menu-code ("C") and a fast-path sub-route ("garantia").

**Synthesis:** This is a well-crafted domain-expert agent. The prompt establishes a precise professional identity, gives the executing agent enough IFPUG vocabulary to make judgment calls on ambiguous DER/RLR/ALR counts, and pushes deterministic work (complexity matrices, source validation) to scripts. No waste patterns, no back-references, no wall-of-text blocks detected in pre-pass, and manual inspection confirms none. The main craft risks are minor: absence of an explicit progression/completion signal in the capability prompt, and a potential structural concern that the capability prompt contains large inline templates that could migrate to `./templates/`.

## Prompt Health Summary

- Total prompt files: 2 (1 SKILL.md + 1 capability)
- Config headers present: 2/2 (SKILL.md On Activation resolves vars; capability has explicit "Config note" referring to parent resolution)
- Progression conditions present: 0/2 (pre-pass detected none; not critical for a single-capability agent that ends with an explicit "Stop" / exit-code contract)
- Self-contained: Yes. `count-capability.md` restates prerequisites implicitly (lists required inputs in Passo 1), contains the full Fast-Path logic, and defines Headless Mode locally. Would survive compaction of SKILL.md.
- Waste patterns (pre-pass): 0
- Back-references: 0
- Suggestive loading: 0
- Wall-of-text: 0

## Per-Capability Craft

### CONTAGEM — `references/count-capability.md` (Code C)

- **Outcome-driven:** Yes. "What Success Looks Like" (lines 13-18) names the two concrete artifacts and the two hard invariants (zero orphans; matrix-derived classification).
- **Voice alignment:** Maintains the precise, IFPUG-vocabulary register established in SKILL.md. No conflicting tone.
- **Intelligence placement:** Correct. Arithmetic and matrix lookup are delegated to `calculate-fp.py`; orphan detection is delegated to `validate-fp-sources.py`; the prompt holds judgment (what counts as a DER, whether a case-use is EE vs SE vs CE, when to pause for ambiguity).
- **Context sufficiency:** Each step gives the agent enough framing to improvise (e.g., Passo 2 explains ALI vs AIE distinction, Passo 3 explains EE/SE/CE boundaries, Regra anti-duplicacao is stated explicitly).
- **Dual-mode contract:** Headless Mode (lines 192-198) and Interactive Mode (lines 200-204) are both specified with clear behaviors. Exit codes align with SKILL.md Headless Contract.
- **Fast-path:** Correcao em Garantia (lines 20-47) is a clean short-circuit with literal template output — appropriate given the contractual-zero-PF nature.

**No over-specification detected.** The step-by-step structure is legitimate: IFPUG counting is a genuine multi-step procedure where order matters (data functions must exist before transactional ALR counts can be computed, brutos must precede VAF).

## Key Findings

### Low — Missing explicit progression/completion conditions

- **File:** `SKILL.md:58-64` (Capability Routing) and `references/count-capability.md` end.
- **Issue:** Pre-pass reports `prompts_with_progression: 0`. The capability ends without an explicit "When complete:" / progression signal beyond the fast-path's literal `Stop` and the Headless Mode exit-code reference.
- **Why it matters:** For stateless single-capability agents with a strong Headless Contract, this is low-risk — but a one-line "When both artifacts are written and `validate-fp-sources.py` reports zero orphans, announce completion with PF Brutos and PF Ajustado, then stop." would make termination unambiguous in interactive mode.
- **Fix:** Add a terminal "## Completion" section to `count-capability.md` after line 204 stating the success exit behavior for interactive mode.

### Low — Inline artifact templates in capability prompt

- **File:** `references/count-capability.md:128-190` (Passo 7 output templates) and `:28-45` (fast-path templates).
- **Issue:** ~75 lines of literal markdown templates for `contagem-detalhada.md` and `resumo-apf.md` live inside the capability prompt.
- **Why it matters:** Templates are deterministic structure; they would be equally effective as files in `./templates/` with the prompt referencing them. Keeping them inline is acceptable at this size (205 lines total) but would become a concern if additional capabilities are added. Not genuine waste today — just a structural preference.
- **Fix (optional):** Extract to `./templates/contagem-detalhada.tmpl.md` and `./templates/resumo-apf.tmpl.md` if the agent grows. Leave inline otherwise.

### Note — Headless ambiguity exit-code convention

- **File:** `SKILL.md:70-73` vs `references/count-capability.md:197`.
- **Observation:** SKILL.md says exit 1 means "artefatos invalidos ou funcoes orfas"; capability says exit 1 also applies when pending classifications remain. These are compatible (both are "invalid/blocked" states) but the mapping could be made explicit. Not a defect.

## Strengths (Worth Preserving)

1. **Overview mission statement (SKILL.md:14)** — "Toda funcionalidade entregue tem sua medida em Pontos de Funcao auditavel, rastreavel a requisito, e classificada deterministicamente segundo IFPUG." This is load-bearing persona DNA; it shapes every judgment call the agent makes. Do not strip.
2. **Communication Style concrete example (SKILL.md:23)** — The "ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF" example teaches output format in one line. High-leverage token spend.
3. **Principles tied to observable behavior (SKILL.md:29-33)** — Each of the four principles maps to a testable agent action (run `calculate-fp.py`, cite US/RN, dedupe entities, ask when uncertain). No philosophy-for-philosophy's-sake.
4. **Prerequisite Check with graceful fallback (SKILL.md:44-56)** — Distinguishes hard-block (missing requirements) from soft-block (missing data-model — offer inference option). Good theory of mind.
5. **Fast-path isolation (count-capability.md:20-47)** — The Correcao em Garantia branch is a genuine contractual short-circuit; encoding it as a fast-path prevents wasted IFPUG analysis on zero-PF work.
6. **Intelligence placement** — All arithmetic and source validation delegated to scripts; all judgment (classification, ambiguity handling, interlocutor communication) retained in prompts. Textbook separation.
7. **Bilingual register** — SKILL.md/capability are in Portuguese for user-facing content while structural keywords stay in English where conventional. Consistent and intentional.

## Overall Craft Verdict

Well-crafted domain-expert agent with no high or critical issues. The two low findings are optional polish. Total token footprint (3272) is appropriate for a single-capability IFPUG counting agent with strong rastreabilidade guarantees.
