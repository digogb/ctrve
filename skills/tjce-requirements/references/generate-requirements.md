---
name: generate-requirements
description: Core capability for generating the four mandatory PDS Unificado requirement artifacts with full traceability.
---

# Gerar Especificacao de Requisitos

Produce the four mandatory PDS Unificado artifacts as a cohesive, fully traceable set. All artifacts are generated together — never in isolation — because traceability constraints require cross-artifact consistency.

## What Success Looks Like

Four complete markdown files at `{project-root}/spec/requirements/`:

1. **product-vision.md** — Escopo, Fora de Escopo, Premissas, Restricoes
2. **user-stories.md** — Estorias no formato "Como [perfil], quero [acao], para que [valor]"
3. **business-rules.md** — Tabela completa: ID | Descricao | Condicao | Acao | Excecao | Estoria
4. **messages.md** — Tabela completa: Codigo | Tipo | Texto | Regra

Every cell filled. No placeholders. No "TODO". No empty exception columns.

## Traceability Constraints (Non-Negotiable)

These are hard constraints — violating any one invalidates the entire specification:

- Every Business Rule (RN) references at least one User Story (US)
- Every System Message (MSG) references at least one Business Rule (RN)
- Every Business Rule has at least one derivable test case (the rule's Condition + Action + Exception must be specific enough to write a test)
- Messages cover all four types: erro, sucesso, validacao, confirmacao
- All table columns are filled — Excecao column uses "N/A" only when genuinely no exception exists, with brief justification

## Your Approach

### When conducting an interview (interactive mode)

Extract requirements by functional area. For each area, ensure you have enough to produce all four artifacts before moving to the next. The interview is complete when you can fill every cell of every table without assumptions.

Focus questions on: actors and their goals, business rules that govern behavior, what happens when things go wrong (exceptions), and what the user needs to see (messages).

### When generating from a PRD or brief

Read the full document first. Identify functional areas, actors, and business rules. Where the source document is ambiguous or incomplete:

- **In headless mode:** Make the most conservative reasonable assumption and flag it with `[ASSUMIDO]` inline. Generate a `spec/requirements/assumptions.md` listing all assumptions for human review.
- **In interactive mode:** Stop and ask before proceeding.

### Generation Order

Generate in this order — each artifact informs the next:

1. **Product Vision** — establishes scope boundaries (what's in, what's out)
2. **User Stories** — enumerate all actor-goal pairs within scope
3. **Business Rules** — derive rules from stories, ensuring every story has at least one rule
4. **System Messages** — derive messages from rules, ensuring every rule has at least one associated message

### Artifact Formatting

Load `./artifact-templates.md` for the exact markdown structure of each artifact. Follow the templates precisely — format consistency across TJCE projects is a requirement.

## After Generation

### Self-Validation

Before presenting the artifacts, verify:

- [ ] Every RN references at least one US that exists in user-stories.md
- [ ] Every MSG references at least one RN that exists in business-rules.md
- [ ] Every RN has Condition + Action specific enough to derive a test
- [ ] All four message types (erro, sucesso, validacao, confirmacao) are present
- [ ] No cell contains "TODO", "TBD", "a definir", or is empty
- [ ] Product Vision scope aligns with the stories actually specified
- [ ] IDs are sequential and consistent (US-001, RN-001, MSG-001)

If any check fails, fix it before outputting. If fixing requires information you don't have, ask (interactive) or flag as `[ASSUMIDO]` (headless).

### Output Summary

After writing the files, present a traceability summary:

- Total: X User Stories, Y Business Rules, Z Messages
- Coverage: every RN linked, every MSG linked
- Assumptions made (if any)
- Gaps or risks identified during analysis
