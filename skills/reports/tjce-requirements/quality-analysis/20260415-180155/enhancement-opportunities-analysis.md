# Enhancement Opportunities Analysis — tjce-requirements Skill
**Generated:** 2026-04-15 18:01:55
**Scope:** BMad skill at `skills/tjce-requirements/`
**Analyst Model:** claude-sonnet-4-6

---

## Executive Summary

The `tjce-requirements` skill is architecturally sound and well-scoped. Its traceability model (US → RN → MSG) is rigorous and domain-appropriate. However, six user archetypes reveal recurring dead-ends in the interactive path, several dangerous assumption walls in headless mode, and meaningful delight opportunities that would significantly reduce analyst rework cycles. The most critical gap is the absence of a soft gate at the start of the interview — the agent can race into generation with insufficient information and only discover incompleteness during self-validation, which is expensive to recover from.

---

## 1. Edge Case Discovery

### 1.1 Partial PRD / Brief with Mixed Completeness
**Trigger:** User provides a file that is 60% complete — some functional areas are well-described, others have only headings or bullet fragments.

**Current behavior:** The agent reads the full document and proceeds. In headless mode it emits `[ASSUMIDO]` tags. In interactive mode it stops and asks. Neither response specifies *which* areas are complete vs. incomplete before asking, so the user cannot predict how many interruptions are coming.

**Gap:** No upfront completeness scan that maps "this area is ready, this area needs X, this area needs Y" before beginning generation. The user receives interruptions mid-artifact, which breaks their mental model of progress.

**Enhancement:** After loading a PRD/brief, emit a **coverage map** before generation:
```
Analise de cobertura do documento:
  [OK]  Autenticacao — suficiente para gerar artefatos
  [OK]  Protocolo de Peticoes — suficiente
  [LACUNA] Perfis de Acesso — faltam: condicoes de excecao, atores alternativos
  [LACUNA] Integracao PJe — sem detalhes de escopo
Antes de gerar, preciso esclarecer 3 pontos...
```
This is the **intent-before-ingestion** pattern: declare understanding before consuming.

---

### 1.2 System Name / Project Identity Missing
**Trigger:** User provides a brief that describes functionality but never names the system.

**Current behavior:** All four artifact templates require `{Nome do Sistema}` in the title. The agent has no fallback — it will either use a placeholder (violating the no-placeholder principle) or silently infer a name.

**Gap:** Template headers will be inconsistent or wrong across the four files if the name is inferred differently per artifact.

**Enhancement:** Treat system name as a hard prerequisite. If absent from input, ask as the first question regardless of mode. In headless mode, derive the name from the PRD title or filename, flag it as `[ASSUMIDO]`, and document in `assumptions.md`.

---

### 1.3 Scope Boundary Ambiguity
**Trigger:** User provides a description that conflates in-scope and out-of-scope items (e.g., "the system will integrate with PJe and possibly with SEEU in the future").

**Current behavior:** The agent must decide what goes in Product Vision's "Fora de Escopo" section. The word "possibly" is ambiguous.

**Gap:** If the agent guesses wrong, the User Stories and Business Rules derived from scope will be incorrect. In interactive mode the agent should catch this; in headless mode the `[ASSUMIDO]` tag may not surface the full risk of the decision.

**Enhancement:** In headless mode, treat any speculative scope language ("possivelmente", "futuramente", "a avaliar", "pode ser") as an automatic assumption trigger with explicit risk annotation: `[ASSUMIDO: excluido do escopo — linguagem especulativa. Alto risco se esta integracao for obrigatoria para o MVP.]`

---

### 1.4 Single Actor System
**Trigger:** User describes a system with only one actor (e.g., an internal batch processing tool used only by system administrators).

**Current behavior:** User Stories format requires actor-goal pairs. A single actor with multiple goals produces valid stories, but the coverage check "all actors covered" cannot be verified if the agent never enumerated actors.

**Gap:** There is no explicit actor enumeration step before story generation. The agent may omit actor variants (e.g., "Magistrado substituindo" vs. "Magistrado titular") that aren't explicitly stated but are implied by judicial context.

**Enhancement:** Add an actor enumeration micro-step at the start of story generation: list all actors identified, prompt user to confirm or extend. This is particularly important for judicial systems where role hierarchies (magistrado, servidor, advogado externo, administrador de sistema) are implicit domain knowledge.

---

### 1.5 Message Text That Requires Legal Review
**Trigger:** Business rules derived from legal statutes (CNJ resolutions, CPCivil) produce messages that contain legally sensitive language.

**Current behavior:** The agent generates the exact text displayed to the user. For judicial systems, some message text may need legal review before deployment (e.g., deadline warnings, rejection notices with legal basis citations).

**Gap:** No mechanism to flag messages that reference legal norms and may require compliance review.

**Enhancement:** Add a message annotation layer: when a message text references a specific legal norm (identified by patterns like "Art.", "Lei n.", "Resolucao CNJ"), append a review marker in the output summary: `[REVISAO JURIDICA RECOMENDADA: MSG-012 — referencia normativa detectada]`.

---

### 1.6 Contradictory Rules from Different Stakeholders
**Trigger:** User provides a PRD authored by multiple stakeholders, or conducts an interview where answers contradict each other (e.g., "prazo de 5 dias" stated in one area, "prazo de 3 dias" in another for the same process step).

**Current behavior:** The agent generates RNs from the input. Internal contradictions may survive into the artifacts.

**Gap:** No cross-artifact consistency check for numeric values, deadlines, or role assignments across different business rules.

**Enhancement:** During self-validation, add a contradiction scan: for each quantitative constraint (prazo, limite, percentual) and each role-permission pair, verify uniqueness or explicit differentiation. Flag conflicts before output.

---

## 2. Experience Gaps (Dead-Ends, Assumption Walls, Missing Recovery)

### 2.1 The Assumption Wall in Headless Mode
**Scenario:** Headless mode with a sparse brief generates a large `assumptions.md`. The human reviewer sees 15+ `[ASSUMIDO]` entries and must now decide: approve all, reject all, or selectively override.

**Gap:** There is no structured override mechanism. The reviewer cannot say "accept assumptions 1-12, reject assumption 13, provide new value: X" without manually editing generated artifacts.

**Enhancement:** Structure `assumptions.md` as a decision table with an "Override" column:

```markdown
| ID | Arquivo | Localizacao | Assumido | Risco | Override |
|----|---------|-------------|----------|-------|----------|
| A-001 | business-rules.md | RN-003 Excecao | "N/A — regra deterministica" | Baixo | |
| A-002 | product-vision.md | Fora de Escopo | "Integracao SEEU excluida" | Alto | |
```

The reviewer fills the Override column and re-runs with `--apply-overrides assumptions.md`. This creates a **dual-output** pattern: first pass generates + flags, second pass refines.

---

### 2.2 Interview Dead-End: No "I Don't Know Yet" Path
**Scenario:** First-timer conducting an interview reaches a question about exceptions for a business rule. They genuinely don't know — the rule hasn't been fully thought through.

**Current behavior:** The agent is instructed to never use placeholders and never assume. It would presumably keep asking until an answer is provided. There is no stated recovery path for "I don't know."

**Gap:** The interview has no graceful handling of provisional answers. A user who says "nao sei ainda" is stuck in a loop or produces an incomplete artifact.

**Enhancement:** Implement a **deferred item queue**. When the user says "nao sei" or "preciso verificar":
1. The agent marks the item as deferred with a token (e.g., `[PENDENTE-001]`)
2. Continues the interview on other areas
3. At the end of the interview, presents all deferred items as a focused mini-questionnaire
4. Only after all deferred items are resolved does generation proceed

This is the **capture-don't-interrupt** pattern applied to knowledge gaps.

---

### 2.3 No Re-Entry Path After Partial Session
**Scenario:** Expert user starts an interactive session, completes the interview for 3 of 5 functional areas, and has to stop (meeting, end of day). Returns the next day.

**Current behavior:** Sessions are stateless. The interview starts over. No mechanism to resume from a checkpoint.

**Gap:** For large systems (10+ functional areas), this is a significant usability failure. The agent has no concept of session state.

**Enhancement:** At the end of each functional area during the interview, offer to save a checkpoint:
```
Area 'Autenticacao' concluida. Quer salvar um rascunho intermediario antes de continuar?
Salvando em: spec/requirements/draft/session-20260415.json
```
On re-activation, detect draft files and offer to resume. This enables **graceful degradation** for long sessions.

---

### 2.4 Validation Failure After Generation with No Rollback
**Scenario:** The self-validation checklist (post-generation) catches a failure — e.g., an RN references a US that doesn't exist. The artifacts are already partially written.

**Current behavior:** "If fixing requires information you don't have, ask (interactive) or flag as `[ASSUMIDO]` (headless)." But the files may already be on disk in an inconsistent state.

**Gap:** No atomic write guarantee. A user could end up with three complete files and one broken file, with no clear indication of which file failed validation.

**Enhancement:** Use a staging approach: write all four artifacts to a `spec/requirements/.draft/` folder, run full self-validation against the draft set, then move atomically to `spec/requirements/` only on full validation pass. If validation fails, leave the draft in place, present the specific failures, and do not overwrite any previously valid files.

---

### 2.5 Ambiguity Interruption with No Context Window
**Scenario:** The agent stops mid-generation to ask about an ambiguity. The user has scrolled away from the relevant section of the PRD. They need to re-read the source document to answer.

**Gap:** The ambiguity question is presented without quoting the specific source text that triggered it. The user must hunt for context.

**Enhancement:** When raising an ambiguity, always quote the triggering source text:
```
Ambiguidade detectada em business-rules.md — Area: Autenticacao

Fonte (linha 47 do brief): "o sistema deve validar o usuario conforme politica vigente"

Problema: "politica vigente" nao especifica o mecanismo. Interpretacoes possiveis:
  (a) Autenticacao CPF + senha no banco TJCE
  (b) SSO via sistema estadual de identidade
  (c) Certificado digital ICP-Brasil

Qual delas se aplica aqui?
```

---

## 3. Delight Opportunities

### 3.1 Traceability Matrix as a Bonus Artifact
**Current state:** The output summary shows coverage counts (X stories, Y rules, Z messages) as text.

**Opportunity:** Generate a fifth bonus artifact — `traceability-matrix.md` — as a cross-reference table showing every US → RN → MSG linkage in a single view. This is extremely valuable for review sessions with stakeholders who want to validate coverage without reading four separate files.

```markdown
| US | Titulo | RNs Vinculadas | MSGs Vinculadas |
|----|--------|----------------|-----------------|
| US-001 | Autenticar usuario | RN-001, RN-002 | MSG-001, MSG-002, MSG-003 |
```

This is the **parallel review lenses** pattern — the same information presented as a cross-cut view for a different audience.

---

### 3.2 Test Case Hints Embedded in Business Rules
**Current state:** The traceability constraint says every RN must be specific enough to derive a test case, but no test cases are generated.

**Opportunity:** After each business rule, add a collapsed section with auto-derived test case stubs:

```markdown
<!-- TEST HINTS (para equipe de QA)
Dado: {Condicao}
Quando: {Acao}
Entao: resultado esperado derivado da regra
Caso de excecao: {Excecao} → comportamento esperado
-->
```

These are HTML comments, invisible in rendered views but available to the QA team in the raw file. Zero noise for requirements reviewers, high value for testers.

---

### 3.3 Scope Creep Warning During Interview
**Current state:** The interview proceeds linearly through functional areas. If the user keeps adding new actors or use cases, the scope expands silently.

**Opportunity:** Track the initial scope stated in the first pass of the interview. If subsequent answers introduce new actors or functional areas not mentioned initially, surface a gentle scope alert:

```
Observacao: voce mencionou "advogado externo" como ator agora, mas nao foi citado no 
escopo inicial. Confirma que este perfil deve ser incluido? Se sim, revisarei 
a Visao do Produto para refletir isso.
```

This prevents scope creep from corrupting the Product Vision artifact that was generated first.

---

### 3.4 Domain Knowledge Injection for Judicial Context
**Current state:** The agent relies entirely on user-provided information. It does not leverage its knowledge of TJCE-specific context (CNJ resolutions, CPC/2015 procedural timelines, standard judicial actors).

**Opportunity:** Maintain a domain knowledge sidebar. When generating business rules for common judicial workflow patterns (peticionamento, audiencias, cumprimento de sentenca, bloqueio BACENJUD), the agent can offer pre-validated rule templates from CNJ normative references:

```
Identifiquei que esta area cobre "prazo para resposta do reu". 
O CPC/2015 Art. 335 estabelece prazo de 15 dias uteis como padrao.
Deseja usar esse prazo como base para RN-007, ou o sistema tem regra especial?
```

This converts the agent from a transcription tool into a genuine domain-aware analyst.

---

### 3.5 Diff View for Iterative Sessions
**Current state:** If the agent runs on a PRD update (v2), it generates a complete new set of artifacts with no indication of what changed.

**Opportunity:** Detect existing artifacts in the output folder. If found, offer a diff mode:

```
Artefatos existentes detectados em spec/requirements/ (versao anterior).
Modo disponivel:
  [1] Regerar completo (sobrescreve)
  [2] Modo diff — mostra apenas o que mudou, para revisao antes de aplicar
```

In diff mode, present changes as `[ADICIONADO]`, `[ALTERADO]`, `[REMOVIDO]` markers before writing. This is the **dual-output** pattern applied to versioning.

---

## 4. Assumption Audit

The following implicit assumptions are embedded in the current skill design and represent risks:

| # | Assumption | Where | Risk Level | Mitigation |
|---|-----------|-------|-----------|------------|
| A1 | User always works in a single project root with `_bmad/config.yaml` present | SKILL.md — On Activation | Medium | Document fallback behavior when config is absent; currently silent |
| A2 | `{planning_artifacts}` contains at most one PRD/brief | SKILL.md — Input Detection step 4 | High | If multiple files exist, agent behavior is undefined — add disambiguation prompt |
| A3 | The four artifact types always suffice (no additional PDS Unificado artifacts exist or will be added) | generate-requirements.md | Low | Modular template loading means extensions are possible, but no extension point is documented |
| A4 | All four message types (erro, sucesso, validacao, confirmacao) are always derivable from any valid requirements set | generate-requirements.md — Traceability Constraints | Medium | Small, tightly scoped systems (e.g., read-only dashboards) may genuinely have no confirmation messages; the constraint would force artificial confirmations |
| A5 | "N/A" in Exception column is always acceptable when justified | artifact-templates.md | Low | Some internal governance reviewers may reject N/A without further evidence; consider requiring a test that proves the exception is truly unreachable |
| A6 | The user can meaningfully answer all interview questions in a single session | generate-requirements.md — Interview approach | High | See gap 2.2 and 2.3; no session continuity mechanism exists |
| A7 | File paths use the host OS separator and `{project-root}` is resolvable at runtime | SKILL.md — On Activation | Low | Windows/WSL environments may produce path issues; no path normalization is specified |
| A8 | Headless mode input is always well-formed markdown or structured text | SKILL.md — Input Detection step 1 | Medium | PDF exports, Word-to-text conversions, or email-forwarded briefs may arrive malformed; no input sanitization step is defined |

---

## 5. Headless Potential Assessment

**Current headless support:** Basic — requires a PRD, emits `[ASSUMIDO]` tags, generates `assumptions.md`.

**Assessment:** Headless mode is underbuilt relative to the skill's stated ambitions. It functions as a "generate with warnings" mode rather than a truly autonomous analyst mode. The following gaps are specific to headless:

### 5.1 No Quality Score
Headless mode generates artifacts but provides no machine-readable quality signal. An automated pipeline has no way to know if the output required 2 assumptions or 20, or whether any assumptions were high-risk.

**Enhancement:** Generate a `spec/requirements/quality-report.json` alongside the artifacts:
```json
{
  "generated_at": "2026-04-15T18:01:55Z",
  "total_assumptions": 4,
  "high_risk_assumptions": 1,
  "traceability_coverage": {
    "stories_without_rules": 0,
    "rules_without_messages": 0,
    "message_types_present": ["erro", "sucesso", "validacao", "confirmacao"]
  },
  "recommended_human_review": true,
  "review_reason": "1 high-risk assumption detected in scope boundaries"
}
```

### 5.2 No Confidence Gradient on Generated Content
Every cell in every table carries equal apparent authority, regardless of whether it was directly stated in the PRD or inferred by the agent. A reviewer cannot distinguish high-confidence from low-confidence content without reading `assumptions.md` in parallel.

**Enhancement:** In headless mode, support a `--annotate-confidence` flag that adds inline markers: `[DIRETO]` for content directly sourced from input, `[INFERIDO]` for content derived by reasoning, `[ASSUMIDO]` for content with no basis in input.

### 5.3 No `--dry-run` Mode
There is no way to run headless analysis without writing output files. This prevents use in CI pipelines where the goal is validation (does the PRD have enough information to generate?) rather than generation.

**Enhancement:** Add `--dry-run` flag: performs all analysis, prints the coverage map and assumption list to stdout, exits with code 0 (sufficient) or 1 (insufficient), writes no files.

---

## 6. Facilitative Workflow Patterns — Gap Analysis

| Pattern | Status | Assessment |
|---------|--------|-----------|
| **Soft gate elicitation** | Absent | The agent has no soft gate at session start. It will begin generation as soon as it believes it has enough information, without confirming with the user that the scope is correct. Add: "Antes de gerar, confirme: escopo inclui X, Y, Z — correto?" |
| **Intent-before-ingestion** | Partial | In interactive mode with file input, the agent reads and proceeds. It does not first state its interpretation of the document's intent. Add: a brief "Entendi que este sistema faz X para atores Y e Z. Confirma?" before generation begins. |
| **Capture-don't-interrupt** | Absent | Interview mode interrupts immediately on ambiguity. For minor ambiguities (e.g., a label or title question), this is disruptive. Reserve immediate interruption for structural ambiguities; capture cosmetic ones for a deferred pass. |
| **Dual-output** | Absent | No draft/final separation. No diff mode between versions. Both are high-value additions. |
| **Parallel review lenses** | Absent | Single output set with one view. Traceability matrix bonus artifact would address this. |
| **Three-mode architecture** | Partial | Interactive and headless modes exist. Missing: a "review mode" where the agent analyzes *existing* artifacts for completeness and consistency without regenerating. Useful for QA cycles. |
| **Graceful degradation** | Absent | No partial session save, no fallback for ambiguities in headless, no recovery path for "I don't know" answers. |

---

## 7. User Journey Stress Tests

### Journey 1: First-Timer
**Profile:** Product manager from TJCE IT department. Familiar with judicial processes, unfamiliar with PDS Unificado artifacts.

**Stress points:**
- Will not know what "Regras de Negocio" or "Mensagens do Sistema" are as output artifacts — the skill never explains what it is about to produce
- Will not know the interview will be long — no upfront scope estimate ("esta entrevista deve durar aproximadamente X perguntas")
- When the agent asks about exceptions (column "Excecao"), the PM may not understand what level of detail is needed
- **Recommendation:** Add a 3-sentence onboarding preamble when no prior artifacts are detected: explain the four artifacts, estimated interview length, and what happens at the end.

---

### Journey 2: Expert (senior analyst who knows PDS Unificado well)
**Profile:** Has used the skill on 5+ previous projects. Wants fast generation with minimal interruption.

**Stress points:**
- Cannot skip the interview if a brief is provided verbally — must wait for full interview flow
- Cannot customize artifact depth (some experts want more detailed acceptance criteria; others want minimal)
- No "batch mode" to generate multiple systems from a folder of briefs
- **Recommendation:** Support `--fast` flag that assumes all ambiguities are low-risk and only interrupts for structural conflicts. Add `--brief-format` option for minimal acceptance criteria (2 per story instead of full expansion).

---

### Journey 3: Confused User
**Profile:** Developer who was asked to "run the requirements tool" but doesn't understand what input is needed.

**Stress points:**
- With no input and no PRD, the agent begins an interview — but the developer cannot answer domain questions about business rules
- There is no "wrong person" detection: "Parece que voce pode nao ser o stakeholder de negocio mais adequado para esta entrevista. Quer convidar alguem ou continuar?"
- **Recommendation:** Early in the interview, assess if answers suggest the respondent has domain authority. If not, surface a gentle redirect.

---

### Journey 4: Edge-Case (Minimal System)
**Profile:** Analyst for a very small system — a single-page internal lookup tool with one actor, two functions, and no exceptions.

**Stress points:**
- Traceability constraint requires all four message types (erro, sucesso, validacao, confirmacao). A read-only lookup tool may genuinely have only informational messages and errors.
- The agent would be forced to either generate artificial confirmation messages or fail validation.
- **Recommendation:** Allow the four-type constraint to be relaxed with explicit justification: if a system has no state-changing operations, confirmation messages are not applicable. Flag this as a documented exception in the output.

---

### Journey 5: Hostile Environment (Poor Input Quality)
**Profile:** Agent runs in CI against a PRD that is auto-generated from a Jira export — fragmented, inconsistent terminology, mixing Portuguese and English, duplicate sections.

**Stress points:**
- No input normalization: the agent will treat "User Story" and "Estoria de Usuario" as potentially different concepts
- Duplicate section detection: if the PRD has the same functional area described in two places with different details, the agent may generate conflicting rules
- Mixed-language input producing Portuguese output may leave untranslated fragments in `{text}` fields
- **Recommendation:** Add a pre-processing step in headless mode: normalize terminology (map known English/Portuguese equivalents), detect duplicate sections (flag for deduplication), warn on mixed-language input.

---

### Journey 6: Automator
**Profile:** DevOps engineer integrating the skill into a CI/CD pipeline that validates requirement completeness on every PRD commit.

**Stress points:**
- No exit code semantics defined — the pipeline cannot distinguish "generated successfully" from "generated with high-risk assumptions" from "failed"
- No machine-readable output summary — the traceability summary is prose, not JSON
- `assumptions.md` format is not specified as a stable schema — it may change, breaking downstream parsers
- The `--headless` flag is the only automation affordance; there is no `--output-format json` option
- **Recommendation:** Define a stable JSON schema for `quality-report.json`, document exit codes (0 = clean, 1 = assumptions present, 2 = validation failure, 3 = insufficient input), and add `--output-format` flag.

---

## 8. Priority Ranking

| Priority | Enhancement | Effort | Impact |
|----------|-------------|--------|--------|
| P0 | Deferred item queue ("nao sei" recovery path) | Low | Critical — blocks first-timers and confused users |
| P0 | Pre-generation coverage map (intent-before-ingestion) | Low | Critical — prevents mid-generation interruptions |
| P1 | Staging/atomic write with rollback on validation failure | Medium | High — prevents inconsistent artifact sets |
| P1 | `quality-report.json` for headless mode | Low | High — unblocks automator archetype |
| P1 | Exit code semantics for headless mode | Low | High — required for CI integration |
| P2 | Traceability matrix bonus artifact | Low | High — delight for stakeholder reviews |
| P2 | Assumption override table in `assumptions.md` | Medium | High — reduces rework in headless cycles |
| P2 | Ambiguity questions with source text quotes | Low | Medium — reduces context-switching friction |
| P3 | Scope creep warning during interview | Medium | Medium — prevents artifact inconsistency |
| P3 | Domain knowledge injection (CNJ/CPC references) | High | High — differentiates from generic analyst |
| P3 | Session checkpoint / resume | High | Medium — mainly benefits large system analysts |
| P4 | Four message type constraint relaxation for minimal systems | Low | Low-Medium — edge case but correctness issue |
| P4 | `--dry-run` mode | Low | Medium — primarily for CI/CD pipelines |
| P4 | Test case hints as HTML comments | Low | Medium — zero-cost delight for QA teams |

---

## 9. Quick Wins (Implementable in a Single Edit Pass)

1. **Add onboarding preamble** (3 sentences) when no artifacts exist and no input is provided — helps first-timers without affecting expert flow.
2. **Quote source text** in every ambiguity interruption — one-line addition to the ambiguity handling instruction.
3. **System name as hard prerequisite** — add explicit check before any generation starts.
4. **Speculative scope language detection** — add a list of trigger phrases to the headless assumption logic.
5. **Add exit code table** to SKILL.md headless documentation — pure documentation, zero behavioral change.

---

*Analysis produced by DreamBot edge-case evaluation framework — 2026-04-15.*
