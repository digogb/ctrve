# Agent Cohesion Analysis — tjce-agent-docs

## Assessment

This is a tightly cohesive, single-purpose agent with a clear identity and a well-matched set of capabilities. The "patient, didactic technical writer" persona aligns naturally with its sole capability of generating end-user manuals from requirement artifacts. The agent feels authentic and purposeful — it knows what it is, who its audience is, and what it refuses to do (invent screens, use jargon). The narrow scope is a deliberate strength, not a limitation.

## Cohesion Dimensions

### 1. Persona-Capability Alignment — Strong

The identity as a "redator tecnico didatico e paciente" is perfectly reflected in the capability design. The communication style rules (imperative tone, zero jargon, functional equivalents for technical terms) are operationalized directly in the manual generation steps. The persona's refusal to invent information is codified as a concrete principle ("Nunca inventar tela") and enforced through the headless mode marking system. There is no gap between who the agent claims to be and what it can do.

### 2. Capability Completeness — Moderate

The agent has one capability (MANUAL) and it covers the full generation workflow well: inventory US, map screens, map messages, draft, validate, write. However, there are noticeable gaps in the lifecycle:

- **No update/incremental capability.** If the manual already exists and new user stories are added, the user must regenerate from scratch. An incremental update mode would be natural for this agent.
- **No export/format conversion.** The output is always Markdown. A judicial institution might need PDF or DOCX. While this could be considered out of scope, an agent producing institutional manuals should at least acknowledge format needs.
- **No glossary generation.** Given the heavy emphasis on translating technical terms to functional equivalents, a standalone glossary capability would be a natural fit.

### 3. Redundancy Detection — Strong

No redundancies detected. The agent has a single capability with a clear six-step process. Each step has a distinct purpose. The SKILL.md and the capability prompt complement each other without overlapping — SKILL.md handles activation, prerequisites, and routing; the capability prompt handles execution detail.

### 4. External Skill Integration — Strong

The agent references `tjce-agent-requirements` as the upstream dependency for generating `user-stories.md` and `messages.md`. This is a clean, documented dependency with a clear handoff point. The agent does not require any skill to be loaded at runtime — it only requires their output artifacts. This is good design: the agent is self-contained but pipeline-aware.

### 5. Capability Granularity — Strong

The single MANUAL capability is at the right level of abstraction. It is not so granular that the user must orchestrate micro-steps, nor so broad that it is unclear. The internal six-step process provides structure without fragmenting into separate capabilities. The Goldilocks test is passed cleanly.

### 6. User Journey Coherence — Moderate

The happy path is well-supported: prerequisites check, optional screen pre-pass, manual generation, validation. However:

- **Entry point is clear** — activation checks prerequisites and routes directly.
- **Interactive recovery is good** — agent asks for missing screen info instead of failing silently.
- **Exit point is useful** — produces a concrete artifact with structured JSON summary.
- **Gap: no review/refinement loop.** After the first generation, the agent offers to read sections aloud but has no structured capability for iterating on the manual (e.g., "rewrite section 3.2 to be simpler" or "add a section for US-045 that was just implemented"). The user must rely on ad-hoc conversation.

## Per-Capability Cohesion

### MANUAL — Gerar Manual do Usuario

**Fit: Excellent.** This is the core and only capability, and it is the natural and obvious thing this agent should do. A technical writer that produces user manuals is about as aligned as it gets. The capability prompt is thorough: it defines inputs, output structure, step-by-step generation process, validation checklist, headless behavior, and interactive behavior. The prohibited terms list and substitution table operationalize the persona's zero-jargon principle directly in the generation steps.

**Minor note:** The `extract-screens.py` script is a supporting tool, not a separate capability, and it is correctly positioned as an optional pre-pass rather than a standalone feature. This is good design.

## Key Findings

### Finding 1 — No incremental update capability

- **Severity:** Medium
- **Affected area:** Capability completeness / User journey
- **What is off:** If the manual already exists and requirements evolve (new US added, messages changed), the entire manual must be regenerated. For a real judicial project where requirements change incrementally across sprints, this creates unnecessary rework.
- **Suggestion:** Add an UPDATE sub-mode or flag (`--update`) that reads the existing manual, diffs against current requirements, and updates only changed/new sections. This aligns naturally with the agent's identity as a patient, meticulous writer who maintains living documentation.

### Finding 2 — No coverage report as standalone output

- **Severity:** Low
- **Affected area:** Capability completeness
- **What is off:** The validation step (Passo 5) checks coverage internally, and the JSON summary includes counts, but there is no way for the user to request just the coverage analysis without generating the full manual. A quick "which US are covered, which are missing screen info?" report would be useful for planning.
- **Suggestion:** Consider a lightweight COVERAGE check mode that runs steps 1-3 and the validation checklist without generating the full manual text.

### Finding 3 — Screen extraction limited to React/Next.js

- **Severity:** Low
- **Affected area:** Capability completeness / External integration
- **What is off:** The `extract-screens.py` script is hardcoded for React/Next.js (JSX/TSX patterns, Next.js pages directory). If a TJCE project uses Angular, Vue, or another framework, the pre-pass produces nothing. The agent handles this gracefully (falls back to requirements-only mode), but it is worth noting.
- **Suggestion:** Document the React/Next.js assumption explicitly in SKILL.md. If other frameworks are likely, the script could be extended or parameterized.

### Finding 4 — Business rules integration is underspecified

- **Severity:** Suggestion
- **Affected area:** Capability completeness
- **What is off:** `business-rules.md` is listed as an optional input that "enriches the manual," but the generation steps never explicitly describe how business rules are incorporated. Step 3 maps messages but there is no analogous step for business rules.
- **Suggestion:** Add a brief sub-step in Passo 3 or between Passo 3 and 4 that describes how to weave business rules into the manual (e.g., as explanatory notes under validation messages, or as a "Regras importantes" subsection per functionality).

## Strengths

- **Razor-sharp identity.** The agent knows exactly what it is and what it refuses to do. The zero-jargon principle with a concrete prohibited-terms list and substitution table is exemplary — it turns a vague principle into enforceable rules.
- **Clean pipeline design.** The dependency on `tjce-agent-requirements` output artifacts (not on the agent itself) means the agent is self-contained and testable. The prerequisite check with clear error messages and guidance is user-friendly.
- **Headless mode is well-designed.** Exit codes, structured JSON summary, and graceful degradation (marking unknown screens instead of failing) show maturity. This agent can run in CI/CD pipelines, which is unusual and valuable for a documentation agent.
- **Interactive recovery is natural.** Asking the user for screen info when it is missing, rather than silently skipping or inventing, is perfectly aligned with the "patient" and "never invents" persona traits.
- **Supporting tooling (extract-screens.py) is well-scoped.** It does one thing, has tests, and is positioned as optional. It does not over-engineer the screen extraction problem.
- **The manual structure template is practical and institution-appropriate.** Sections like "Acesso ao Sistema" and "Perguntas Frequentes" reflect real needs of court users, not generic documentation templates.

## Creative Suggestions

1. **Accessibility annotations.** Given the judicial/institutional context, the agent could flag or generate accessibility notes (e.g., "This screen can be navigated using keyboard only" or "Screen reader users: the main content starts after the navigation menu"). This would be unique and valuable for a government system.

2. **Version diff narrative.** When the manual is regenerated, produce a brief "O que mudou nesta versao" section at the top listing new, modified, and removed functionalities. This helps institutional users who receive updated manuals understand what changed without reading the whole document.

3. **Complexity scoring per section.** The agent could flag sections where the step count is high (>8 steps) or where multiple messages can appear, suggesting to the development team that the UX might be too complex for the target audience. This turns the documentation agent into a subtle UX feedback mechanism.

4. **Integration with screenshot automation.** The agent already places `[Imagem: {descricao}]` placeholders. A companion script that takes a route list and uses Playwright/Puppeteer to capture screenshots could close the loop, producing a fully illustrated manual from a single pipeline run.
