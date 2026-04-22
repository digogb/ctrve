# Enhancement Opportunities Analysis — tjce-agent-docs

**Scanner:** DreamBot (Creative Edge-Case & Experience Innovation)
**Agent:** tjce-agent-docs — Technical Writer TJCE
**Date:** 2026-04-16

---

## Agent Understanding

This agent is a didactic technical writer that transforms user stories and system message catalogs into a user manual (`manual-usuario.md`) for TJCE judicial systems. Its audience is non-technical court staff — judges, clerks, lawyers — who need step-by-step instructions written in plain Brazilian Portuguese with zero developer jargon. The agent has a single capability (manual generation), supports headless mode with exit codes and JSON summaries, and optionally uses a Python screen-extraction script to map frontend components to user-facing labels and buttons.

**Key assumptions:** Users have pre-generated requirement artifacts from a sibling skill (`tjce-agent-requirements`). The frontend is React/Next.js. The manual fits in a single markdown file. One session produces the complete manual.

---

## User Journeys

### First-Timer

A court staff member or junior developer is told "generate the user manual" but has never used Claude Code or any agent skill before.

**Friction points:**
- The agent references `tjce-agent-requirements` if prerequisites are missing, but gives no guidance on how to invoke that skill — the user is told what to do but not how
- The `extract-screens.py` pre-pass is described as "optional efficiency boost" but there is no guidance on when to run it vs. skip it; a first-timer will not know the tradeoff
- The `{output_folder}` and `{project-root}` resolution depends on config files (`_bmad/config.yaml`) whose existence and format are not explained

**Bright spots:**
- The prerequisite check is clear and stops early with an actionable message
- The agent's identity as "quem explica para um colega leigo" sets a welcoming tone

### Expert

A senior developer who has written manuals before and knows exactly what the system does.

**Friction points:**
- Single capability with no fast-track. An expert who already has screen knowledge in their head cannot pass it inline — they must either run the Python script or answer questions one-by-one about each screen
- No way to provide a partial manual and ask the agent to complete/update only missing sections. It is always a full generation
- No `--dry-run` mode to preview the US-to-section mapping before committing to a full generation

**Bright spots:**
- Headless mode with `--json` is well-designed for pipeline integration
- The structured exit codes (0/1/2) are clear and actionable

### Confused User

Someone who invoked this skill thinking it generates developer documentation or API docs.

**Friction points:**
- The SKILL.md description says "Manual do Usuario" but the skill trigger phrase also mentions "end-user documentation" — someone wanting developer docs might invoke this and be confused when the output has zero technical content
- No early intent check: the agent does not ask "what kind of documentation do you need?" — it assumes manual-usuario and proceeds

**Bright spots:**
- The strong identity ("nunca usa jargao tecnico") would quickly signal to a confused user that this is not the right tool

### Edge-Case User

Valid but unexpected inputs: a `user-stories.md` with 200+ stories, stories written in English, stories with no screen interaction at all, or a `messages.md` with duplicate message codes.

**Friction points:**
- No guidance on handling very large story sets — will the agent try to generate all 200 sections in one pass? Context window limits could truncate the manual silently
- If `user-stories.md` is written in English (or mixed language), the agent has no language detection or normalization — it might produce a manual mixing Portuguese instructions with English story content
- Duplicate message codes in `messages.md` would produce duplicate explanations with no dedup

### Hostile Environment

Files missing, malformed, or the Python script fails.

**Friction points:**
- The `extract-screens.py` script exits 1 if no screen files are found, but SKILL.md says the screen inventory is optional. If the user runs the script and it exits 1, they may think the agent cannot proceed
- If `user-stories.md` exists but is empty or malformed (no US identifiers, no standard format), the agent has no documented recovery — it will likely produce an empty or incoherent manual
- No file encoding handling in the manual generation step (the Python script handles UTF-8 with error replacement, but the agent's reading of markdown files has no equivalent safeguard)

**Bright spots:**
- The three-tier degradation (screen inventory available / frontend source available / neither) is well-designed

### Automator

A CI pipeline or another agent that invokes this skill headlessly.

**Friction points:**
- The headless contract does not specify how to pass the `--project` name programmatically when there is no `config.yaml` — the JSON output has a `"project"` field but no documented default
- No machine-readable progress indicator during generation — a long-running headless invocation gives no signal until completion
- The `{tmp}` path for `screens.json` is not specified in the headless contract — an automator does not know where to write the pre-pass output so the agent can find it
- No documented way to provide screen information as input parameters in headless mode (e.g., passing a pre-built `screens.json` path)

**Bright spots:**
- Exit codes, JSON summary, and the `--json` flag are exactly what an automator needs
- The clear file path contract (`{output_folder}/manual/manual-usuario.md`) makes downstream consumption predictable

---

## Headless Assessment

**Level: Headless-ready**

This agent is already well-designed for headless operation. The headless contract with exit codes, JSON summary, and graceful degradation for missing screens is solid. Minor gaps prevent it from being fully seamless:

| Interaction Point | Headless Resolution | Gap |
|---|---|---|
| Missing screen info | Already handled — marks with placeholder | None |
| Project name | Could come from `--project` arg | Default is undocumented |
| Screen pre-pass output location | Could be passed as `--screens-json <path>` | `{tmp}` path is ambiguous |
| Manual review offer | Skipped in headless | None |
| Very large story set causing context overflow | No chunking strategy | Medium gap — could produce truncated output silently |

**Suggested additions:**
- Document the `--screens-json <path>` parameter to let automators pass pre-computed screen inventories
- Add a `--project` default (e.g., derive from `config.yaml` or directory name)
- Add a `--output-dir` override for CI pipelines that do not use `_bmad/config.yaml`

---

## Key Findings

### High-Opportunity

**1. No Incremental Update Mode**
- **Area:** Core capability
- **Observation:** The agent always generates the complete manual from scratch. In real projects, user stories are added over sprints. Regenerating the entire manual for one new story is wasteful and risky (could overwrite manual edits to previous sections).
- **Suggestion:** Add an `--update` mode that reads an existing `manual-usuario.md`, identifies which US sections are already present, and generates only new or changed sections. In interactive mode, ask: "Encontrei um manual existente com N secoes. Deseja atualizar apenas as secoes novas ou regenerar tudo?"

**2. No Strategy for Large Story Sets**
- **Area:** Scalability / context management
- **Observation:** A real TJCE system could have 50-200+ user stories. Generating all sections in a single conversation will likely exceed context window limits, causing silent truncation or degraded quality in later sections.
- **Suggestion:** Implement a chunking strategy — generate in batches of 15-20 US, writing each batch to the output file incrementally. In headless mode, this is transparent. In interactive mode, report progress: "Gerando secoes 1-20 de 85..."

**3. Undefined `{tmp}` Path for Screen Inventory**
- **Area:** Headless contract / automation
- **Observation:** The screen pre-pass writes to `{tmp}/screens.json` and the manual generation reads from it, but `{tmp}` is never defined in the config system. An automator cannot reliably wire these together.
- **Suggestion:** Define `{tmp}` as `{output_folder}/.tmp` or accept an explicit `--screens-json <path>` parameter. Document this in the headless contract.

### Medium-Opportunity

**4. No Coverage Report in Interactive Mode**
- **Area:** Exit satisfaction / success awareness
- **Observation:** In headless mode, the JSON summary provides a clear coverage report (total sections, complete, pending, messages covered). In interactive mode, the agent only offers to "read a section aloud" — it does not surface the coverage summary.
- **Suggestion:** After generation, present a coverage dashboard: "Manual gerado: 34 secoes completas, 3 pendentes (US-045, US-067, US-089), 28/31 mensagens cobertas. Deseja revisar as secoes pendentes?"

**5. No Jargon Validation Step**
- **Area:** Quality assurance
- **Observation:** The capability document lists prohibited technical terms and substitutions, but there is no explicit validation pass. The agent relies on its own discipline to avoid jargon, which is inherently unreliable with LLMs.
- **Suggestion:** Add a post-generation scan step: grep the output for the prohibited terms list. Report any violations before finalizing. This could be a simple regex check, similar in spirit to the extract-screens.py script.

**6. Missing Intent-Before-Ingestion Pattern**
- **Area:** User experience / facilitative workflow
- **Observation:** The agent jumps straight to prerequisite checking and artifact ingestion without understanding why the user is here. A user might want to update one section, preview the structure, check coverage without generating, or generate for a subset of stories.
- **Suggestion:** Add a brief intent check before ingestion: "O que voce gostaria de fazer? (1) Gerar o manual completo, (2) Atualizar secoes especificas, (3) Verificar cobertura de US e mensagens, (4) Visualizar a estrutura planejada"

**7. Screen Script Does Not Handle Vue/Angular/Svelte**
- **Area:** extract-screens.py portability
- **Observation:** The script hardcodes React/Next.js patterns (JSX, Route components, etc.). If a TJCE project uses a different framework, the script silently produces zero results (exit 1), which could mislead users into thinking there are no screens.
- **Suggestion:** Add framework detection (check for `package.json` dependencies) and emit a clear warning: "Detected Vue.js project — screen extraction currently supports React/Next.js only. Manual will be generated from requirements only."

### Low-Opportunity

**8. No Screenshot Integration Workflow**
- **Area:** Delight / completeness
- **Observation:** The manual includes `[Imagem: {descricao da tela}]` placeholders for screenshots, but there is no guidance on how to actually capture and link them. The placeholder format is not a standard image reference.
- **Suggestion:** Use standard markdown image syntax with a descriptive alt-text: `![Tela de cadastro de processos](./screenshots/US-001-cadastro.png)` and optionally generate a `screenshots-needed.md` checklist for the team.

**9. No FAQ Auto-Generation Signal**
- **Area:** Manual completeness
- **Observation:** Step 4 says to "derive FAQs from the most probable doubts based on flows" but provides no heuristic for which flows generate FAQs. This is entirely left to LLM judgment, which may produce generic or unhelpful FAQs.
- **Suggestion:** Add explicit FAQ triggers: login/authentication flows always get FAQ entries, any flow with more than 2 validation messages gets a "common errors" FAQ, any flow with role-based access gets a "permissions" FAQ.

**10. No Glossary Section**
- **Area:** Manual completeness
- **Observation:** The manual structure has no glossary, yet TJCE judicial systems likely use domain-specific legal terms (autos, peticionamento, distribuicao) that non-legal staff may not know.
- **Suggestion:** Add an optional "Glossario" section at the end of the manual structure, populated from domain terms found in user stories that may need explanation for general court staff.

---

## Top Insights

1. **Incremental generation is the single most impactful missing feature.** Real projects iterate over sprints. An agent that can only generate the entire manual from scratch forces users to choose between regenerating (losing manual edits) or maintaining the manual by hand (losing the agent's value). An `--update` mode with diff-awareness would transform this from a one-shot tool into a continuous documentation companion.

2. **The agent is remarkably close to being a first-class CI citizen, but the `{tmp}` ambiguity and missing `--screens-json` parameter create a gap.** Fixing these two small contract issues would let this agent slot cleanly into a `generate-requirements -> extract-screens -> generate-manual -> publish` pipeline with zero human touch.

3. **Context window limits are the silent killer for this agent.** A 100-story system will produce a manual that simply cannot be generated in one pass. Without an explicit chunking strategy, the agent will degrade unpredictably on real-world projects, and the user will not understand why later sections are worse than earlier ones.

---

## Facilitative Patterns Check

| Pattern | Present? | Assessment |
|---|---|---|
| **Soft Gate Elicitation** | Partially | The interactive mode asks about missing screens, but uses direct questions rather than "anything else?" soft gates. Not critical for this single-capability agent. |
| **Intent-Before-Ingestion** | Missing | The agent scans artifacts immediately. Adding intent detection would enable subset generation, coverage checks, and update mode. **High opportunity.** |
| **Capture-Don't-Interrupt** | Not applicable | Single-capability, structured generation — users are not in creative discovery flow. |
| **Dual-Output** | Present | The `--json` flag provides an LLM-optimized summary alongside the human manual. Well done. |
| **Parallel Review Lenses** | Missing | The manual is generated and offered for review, but no multi-perspective validation (e.g., a "jargon scanner" lens + a "coverage completeness" lens + a "readability" lens). **Medium opportunity** — even a single automated jargon scan would add value. |
| **Three-Mode Architecture** | Partially | Has interactive and headless modes. Missing a "yolo/autonomous" mode that would generate without stopping on missing screens (currently, headless does this, but interactive always stops). Could add `--skip-missing` for interactive mode. |
| **Graceful Degradation** | Present | Three-tier fallback for screen info (inventory -> source -> requirements-only) is well-designed. |
