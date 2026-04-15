---
name: generate-requirements
menu-code: GR
description: Core capability for generating the four mandatory PDS Unificado requirement artifacts with full traceability.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{planning_artifacts}`, `{communication_language}`, and `{document_output_language}` are resolved by the parent SKILL.md at activation time.

# Gerar Especificacao de Requisitos

Produce the four mandatory PDS Unificado artifacts as a cohesive, fully traceable set. All artifacts are generated together — never in isolation — because traceability constraints require cross-artifact consistency.

## What Success Looks Like

Four complete markdown files at `{output_folder}/requirements/`:

1. **product-vision.md** — Escopo, Fora de Escopo, Premissas, Restricoes
2. **user-stories.md** — Estorias no formato "Como [perfil], quero [acao], para que [valor]"
3. **business-rules.md** — Tabela completa: ID | Descricao | Condicao | Acao | Excecao | Estoria
4. **messages.md** — Tabela completa: Codigo | Tipo | Texto | Regra

Plus a bonus artifact:

5. **traceability-matrix.md** — Cross-reference table showing every US to RN to MSG linkage in a single view

Every cell filled. No placeholders. No "TODO". No empty exception columns.

## Traceability Constraints (Non-Negotiable)

These are hard constraints — violating any one invalidates the entire specification:

- Every Business Rule (RN) references at least one User Story (US)
- Every System Message (MSG) references at least one Business Rule (RN)
- Every Business Rule has at least one derivable test case (the rule's Condition + Action + Exception must be specific enough to write a test)
- Messages cover all four types: erro, sucesso, validacao, confirmacao — unless the system has no state-changing operations, in which case document the exception explicitly in the output summary
- All table columns are filled — Excecao column uses "N/A" only when genuinely no exception exists, with brief justification

## Onboarding (first-timers only)

If no existing artifacts are found at `{output_folder}/requirements/` and the user appears unfamiliar with PDS Unificado, present a brief preamble before starting:

> Este agente gera 4 artefatos obrigatorios do PDS Unificado: (1) Visao do Produto — escopo e limites, (2) Estorias de Usuario — o que cada ator precisa fazer, (3) Regras de Negocio — as condicoes e acoes do sistema, (4) Mensagens — textos exibidos ao usuario. Vou conduzir uma entrevista por area funcional. Ao final, todos os artefatos serao gerados com rastreabilidade completa.

Skip this if the user demonstrates PDS Unificado fluency.

## Your Approach

### When conducting an interview (interactive mode)

Extract requirements by functional area. For each area, ensure you have enough to produce all four artifacts before moving to the next. The interview is complete when you can fill every cell of every table without assumptions.

Focus questions on: what happens when things go wrong (exceptions), and what the user needs to see (messages). These are the areas where domain-specific knowledge is most needed — actors and goals are usually clear from context.

**Handling "nao sei" answers:** If the user cannot answer a question, mark the item as `[PENDENTE-NNN]` and continue the interview on other areas. At the end of the interview, present all deferred items as a focused mini-questionnaire. Only proceed to generation when all deferred items are resolved.

**Scope creep detection:** Track the actors and functional areas mentioned in the first pass of the interview. If subsequent answers introduce new actors or areas not mentioned initially, surface an alert: "Voce mencionou [novo ator/area] agora, mas nao foi citado no escopo inicial. Confirma inclusao?"

### When generating from a PRD or brief

Read the full document first. Identify functional areas, actors, and business rules. If the source document is ambiguous or incomplete:

- **If headless mode:** Make the most conservative reasonable assumption and flag it with `[ASSUMIDO]` inline. Treat speculative scope language ("possivelmente", "futuramente", "a avaliar") as an automatic assumption trigger. Generate `{output_folder}/requirements/assumptions.md` listing all assumptions for human review.
- **If interactive mode:** Stop and ask before proceeding.

**Coverage map (before generation):** After reading the document, emit a coverage assessment per functional area before generating any artifacts:

```
Analise de cobertura do documento:
  [OK]  {area} — suficiente para gerar artefatos
  [LACUNA] {area} — falta: {detalhes especificos}
```

If interactive, resolve gaps before proceeding. If headless, flag as `[ASSUMIDO]` and continue.

### Pre-Generation Scope Confirmation

Before generating artifacts, present a scope summary for confirmation:

- **If interactive:** "Entendi que este sistema faz X para atores Y e Z. Escopo inclui A, B, C. Fora de escopo: D, E. Correto?" Proceed only after confirmation.
- **If headless:** Derive scope from input and include it in the output summary as the interpreted scope.

### Interview-to-Generation Transition

If requirements were gathered through interview, synthesize the dialogue into a compact requirements brief (actors, goals, rules, constraints as bullet lists) before entering the generation phase. Use this brief — not the raw interview transcript — as the working reference for generation.

### Generation Order

Generate in this order — each artifact informs the next. Proceed to the next artifact only when the current one is complete and written to disk:

1. **Product Vision** — establishes scope boundaries (what's in, what's out). Write to disk immediately.
2. **User Stories** — enumerate all actor-goal pairs within scope. Write to disk immediately.
3. **Business Rules** — derive rules from stories, ensuring every story has at least one rule. Write to disk immediately.
4. **System Messages** — derive messages from rules, ensuring every rule has at least one associated message. Write to disk immediately.
5. **Traceability Matrix** — cross-reference table linking US to RN to MSG. Write to disk.

For large systems (50+ user stories), reference the already-written files on disk for cross-artifact traceability checks rather than relying on in-context copies.

### Artifact Formatting

Load `./artifact-templates.md` for the exact markdown structure of each artifact. Follow the templates precisely — format consistency across TJCE projects is a requirement.

## After Generation

### Self-Validation

Do not present artifacts to the user until all checks pass.

**Step 1 — Run the deterministic validator:**

```bash
python3 scripts/validate-artifacts.py {output_folder}/requirements/ --json
```

This script checks: ID sequencing, cross-references (RN→US, MSG→RN), message type coverage, empty/placeholder cells, and N/A justification format. If it returns violations, fix them before proceeding.

**Step 2 — Judgment-based checks** (these require LLM reasoning and cannot be scripted):

- [ ] Every RN has Condition + Action specific enough to derive a test
- [ ] Product Vision scope aligns with the stories actually specified
- [ ] All four message types are present (or exception documented for stateless systems)

If any check fails, fix it before outputting. If fixing requires information you don't have, ask (interactive) or flag as `[ASSUMIDO]` (headless).

### Output Summary

After writing the files, present a traceability summary:

- Total: X User Stories, Y Business Rules, Z Messages
- Coverage: every RN linked, every MSG linked
- Traceability matrix location: `{output_folder}/requirements/traceability-matrix.md`
- Assumptions made (if any), with count and risk level
- Gaps or risks identified during analysis
