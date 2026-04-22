# Structure & Capabilities Analysis — tjce-agent-apf

## Assessment

The agent is structurally sound: all required sections (Overview, Identity, Communication Style, Principles, On Activation) are present, frontmatter is valid, and the single declared capability (`count-capability.md`) exists at the expected location. Identity, principles, and communication style are domain-specific and strong. One pre-pass issue flags a missing "progression condition keyword" in the capability file — this appears to be a false positive given the capability's structure (it has explicit Success Criteria, step-by-step passes, and headless/interactive mode sections), so it is noted as informational rather than as a real defect.

## Sections Found

Required (all present):
- Overview (line 8)
- Identity (line 16)
- Communication Style (line 20)
- Principles (line 28)
- On Activation (line 35)

Optional/structural (all present and well-formed):
- Prerequisite Check (line 44)
- Capability Routing (line 58)
- Headless Contract (line 66)

No invalid sections (no "On Exit" / "Exiting"). No orphaned template placeholders detected.

## Capabilities Inventory

| Code | Capability | Target | Status |
|------|------------|--------|--------|
| C    | CONTAGEM — Contagem Detalhada APF (com fast-path Garantia) | `references/count-capability.md` | Exists, well-structured. Config header present. Includes Success Criteria, fast-path branch (Garantia → PF=0), 7-step detailed flow, Headless Mode, Interactive Mode. Scripts `scripts/calculate-fp.py` and `scripts/validate-fp-sources.py` referenced and exist on disk. |

Single-capability design is appropriate: the domain (IFPUG APF counting) is narrow and the fast-path for Garantia is an internal branch rather than a separate capability — this avoids the "multiple capabilities doing the same thing" anti-pattern.

## Key Findings

### LOW — Pre-pass: "No progression condition keywords" in count-capability.md:205
**File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/references/count-capability.md:205`
**Finding (pre-pass, preserved):** Progression condition keywords not found.
**Assessment:** Likely false positive. The capability file actually progresses via explicit numbered steps ("Passo 1" through "Passo 7"), a clear fast-path conditional ("Se o usuario declara... Correcao em Garantia"), and well-defined success criteria under "What Success Looks Like". It also has explicit Headless Mode exit-code behavior and blocking conditions (Passo 5: "Se houver funcoes orfas... bloqueio"). No action required unless the pre-pass scanner expects specific literal tokens — in which case a minor wording adjustment could satisfy the linter without changing semantics.
**Fix (optional):** If desired for scanner parity, add a short "Progression" or "Stop conditions" line near the end of the capability (e.g., "Prosseguir apenas quando todas as funcoes tiverem fonte validada; bloquear em caso de orfas"). Current semantics already cover this.

### LOW — Headless `--json` summary format not fully specified in SKILL.md
**File:** `/home/rodgb/projetos/ctrve/skills/tjce-agent-apf/SKILL.md:71`
**Finding:** The Headless Contract mentions "structured JSON to stdout when `--json` is passed" but does not define the schema. `count-capability.md:198` lists the expected fields ("total PF brutos, PF ajustado, VAF, contagem por tipo, quantidade de pendentes, is_garantia"), but an explicit JSON schema / example in SKILL.md would make the headless contract fully machine-consumable.
**Fix:** Add a small example JSON block under Headless Contract showing field names/types. Not blocking.

## Strengths

- **Description quality:** Follows the two-part format. Opens with a specific role summary ("Analista de Pontos de Funcao do TJCE segundo IFPUG CPM 4.3.1"), and the trigger clause uses specific quoted-style phrases ("count function points", "perform APF counting", "Correcao em Garantia"). Will trigger reliably and is well-differentiated from generic counting agents.
- **Identity:** Actionable and load-bearing ("Analista de metricas preciso e tecnico que trata cada ponto de funcao como compromisso contratual. Mostra o raciocinio da contagem passo a passo... Nao estima no olho, nao arredonda..."). Directly primes behavior.
- **Communication Style:** Includes concrete IFPUG examples (`"ALI Processo: 8 DER, 2 RLR -> Baixa -> 7 PF"`), language directive, traceability rule, fallback behavior for missing info, and Garantia-specific tone. Five tightly-scoped bullets — exactly the recommended density.
- **Principles:** Domain-anchored and decision-framing. "Determinismo IFPUG", "Rastreabilidade total", "Nao contar em dobro", "Pergunte, nao assuma" each resolve specific APF ambiguities — no generic platitudes.
- **Identity ↔ capabilities ↔ style coherence:** The "passo a passo" promise in Identity is honored by the 7-step flow in the capability and the "raciocinio explicito" example in Communication Style. Strong internal consistency.
- **Activation ordering:** Logical — config resolution, then prerequisite check (blocking), then capability routing, then headless contract. Config vars are defined before being referenced downstream.
- **Prerequisite Check:** Explicit, differentiated fallbacks for each missing artifact (hard stop vs. negotiable), and relaxed rule for Garantia fast-path. Good defensive design.
- **Determinism anchored to scripts:** `calculate-fp.py` is cited as the single source of truth for complexity classification, and `validate-fp-sources.py` enforces traceability. This externalizes non-LLM-safe work to scripts — exactly the right architecture.
- **No over-specification:** Capability file describes WHAT (functions to identify, matrices to apply, artifacts to produce) and delegates HOW for calculation to scripts; does not re-teach LLM basics.

## Memory & Headless Status

- **Memory:** Not a memory agent (`is_memory_agent: false`, no memory paths in pre-pass). Stateless design is appropriate for a counting/measurement agent. No memory setup required.
- **Headless:** Declared and well-specified. Exit codes (0/1/2) cover the expected failure modes; default wake task is implicit via the single capability plus `garantia` fast-path argument; ambiguity-handling rule (`**CLASSIFICACAO PENDENTE**` marker + exit 1) is deterministic. Only gap is the JSON summary schema (see Finding above).

## Summary

No critical or high-severity structural issues. One low-severity pre-pass signal (likely false positive) and one low-severity documentation gap around the headless JSON schema. Agent is ready for runtime use from a structural standpoint.
