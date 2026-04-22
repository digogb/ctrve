# Script Opportunity Analysis — tjce-agent-docs

## Existing Scripts Inventory

| Script | Purpose | Has Tests |
|--------|---------|-----------|
| `scripts/extract-screens.py` | Pre-pass extraction of screen metadata (components, routes, labels, buttons, placeholders, headings) from React/Next.js frontend source. Outputs compact JSON inventory. | Yes (`scripts/tests/test-extract-screens.py`) |

The agent already has one well-designed pre-pass script that handles the most token-expensive deterministic operation: scanning frontend source files. This is a strong foundation.

## Assessment

This agent is reasonably well-partitioned between script and LLM work. The heaviest deterministic operation — scanning frontend source files for UI metadata — is already handled by `extract-screens.py`. However, several medium-weight deterministic operations remain embedded in prompt instructions: prerequisite file existence checks, US inventory extraction from markdown, message catalog parsing, coverage validation (US-to-section mapping and message coverage), and technical jargon detection. These are all rule-based operations that could run as pre-pass or post-pass scripts, saving tokens and improving reliability on every invocation.

## Key Findings

### Finding 1 — Prerequisite File Existence Check (Low)

- **Severity:** Low
- **Affected file:** `SKILL.md:48-52`
- **Current LLM work:** The agent checks whether `user-stories.md`, `messages.md`, and frontend source directory exist, then decides whether to stop or warn.
- **Script alternative:** A Python script using `pathlib.Path.exists()` that checks all prerequisites and emits a JSON status object: `{"user_stories": true, "messages": true, "frontend_src": "/path/or/null", "can_proceed": true}`. The LLM reads the compact status instead of doing filesystem probing.
- **Estimated token savings:** ~80 tokens per invocation (filesystem probing + conditional logic)
- **Pre-pass potential:** Yes — could run before the LLM activates and short-circuit with exit code 2 in headless mode without consuming any LLM tokens at all.
- **Reuse across skills:** High — the pattern of "check artifact prerequisites before activation" applies to any TJCE agent.

### Finding 2 — US Inventory Extraction from user-stories.md (Medium)

- **Severity:** Medium
- **Affected file:** `references/manual-capability.md:79-83` (Passo 1)
- **Current LLM work:** "Ler `user-stories.md`. Identificar todas as US que envolvem interacao de tela (cadastro, consulta, listagem, relatorio, configuracao). Montar lista: `{US-ID, titulo, tipo de interacao}`." The LLM reads the entire user-stories file and extracts a structured inventory.
- **Script alternative:** A Python script that parses `user-stories.md` using regex for US identifiers (e.g., `US-\d+`), extracts titles from headings, and classifies interaction type by keyword matching (cadastro, consulta, listagem, relatorio, configuracao vs. batch/integracao/backend). Outputs JSON: `[{"id": "US-001", "title": "...", "interaction_type": "cadastro", "has_screen": true}]`.
- **Estimated token savings:** ~300-800 tokens per invocation (avoids LLM reading and parsing the full user-stories document for structural extraction; the LLM still reads it for semantic understanding but gets the inventory for free).
- **Pre-pass potential:** Yes — feeds structured data to the LLM so it can skip the inventory-building step and focus on writing.
- **Reuse across skills:** High — any agent consuming `user-stories.md` benefits from a pre-parsed inventory.

### Finding 3 — Message Catalog Parsing from messages.md (Medium)

- **Severity:** Medium
- **Affected file:** `references/manual-capability.md:95-98` (Passo 3)
- **Current LLM work:** "Ler `messages.md`. Para cada mensagem: Identificar em qual US/fluxo ela aparece (pelo contexto ou pelo codigo referenciado)." The LLM reads the full message catalog and extracts structured data (code, text, context, associated US).
- **Script alternative:** A Python script that parses `messages.md` extracting message codes (e.g., `MSG-\d+`), message text, and any US references found in the same section. Cross-references with the US inventory. Outputs JSON: `[{"code": "MSG-001", "text": "...", "context": "...", "related_us": ["US-001"]}]`. The semantic work of writing plain-language explanations stays with the LLM.
- **Estimated token savings:** ~200-500 tokens per invocation (extraction is deterministic; explanation is semantic and stays with LLM).
- **Pre-pass potential:** Yes — the LLM receives a compact JSON catalog instead of raw markdown.
- **Reuse across skills:** Medium — useful for any agent that consumes the TJCE message catalog.

### Finding 4 — Coverage Validation Checklist (Medium)

- **Severity:** Medium
- **Affected file:** `references/manual-capability.md:127-133` (Passo 5)
- **Current LLM work:** Before writing the final artifact, the LLM must verify: (1) every US with screen interaction has a manual section, (2) every message in a user flow is explained, (3) no prohibited technical terms appear, (4) missing-screen sections are marked. This is a four-point validation pass over the generated content.
- **Script alternative:** A post-processing Python script that: (a) takes the generated `manual-usuario.md` plus the pre-extracted US inventory and message catalog, (b) checks that each US-ID from the inventory appears as a section heading, (c) checks that each message code from the catalog appears in the manual, (d) scans for prohibited technical terms using a regex wordlist, (e) counts `TELA NAO IDENTIFICADA` markers. Outputs a validation report JSON.
- **Estimated token savings:** ~400-700 tokens per invocation (the LLM currently re-reads its own output to validate — a script does this deterministically and catches what the LLM might miss).
- **Pre-pass potential:** No — this is a post-pass validator. But equally valuable.
- **Standalone value:** High — could run as a CI lint check on any manual-usuario.md commit.
- **Reuse across skills:** Medium — the technical jargon checker is reusable; the US/message coverage check is TJCE-specific but could be parameterized.

### Finding 5 — Technical Jargon Detection (Medium)

- **Severity:** Medium
- **Affected file:** `references/manual-capability.md:111-124` (prohibited terms list and substitution table)
- **Current LLM work:** The LLM is instructed to never use ~20 technical terms and to substitute them with functional equivalents. This is both a generation constraint and an implicit validation requirement.
- **Script alternative:** A Python script with a wordlist of prohibited terms (API, endpoint, query, schema, frontend, backend, request, response, payload, JSON, token, middleware, componente, rota, render, state, hook, prop, callback) that scans the generated markdown and flags violations with line numbers. Could also suggest substitutions from a mapping dict.
- **Estimated token savings:** ~150-300 tokens per invocation (the validation portion; the LLM still needs the constraint during generation, but post-pass catching is more reliable).
- **Pre-pass potential:** No — post-pass validator.
- **Standalone value:** High — can run as a lint step on any TJCE documentation.
- **Reuse across skills:** High — any TJCE documentation agent benefits from a jargon checker.

### Finding 6 — Headless JSON Summary Generation (Low)

- **Severity:** Low
- **Affected file:** `SKILL.md:80-96` (JSON summary schema)
- **Current LLM work:** In headless mode with `--json`, the LLM must emit a structured JSON summary with counts (total_sections, complete_sections, pending_sections, messages_covered, messages_total).
- **Script alternative:** A post-pass Python script that reads the generated `manual-usuario.md`, counts sections (by heading level), counts `TELA NAO IDENTIFICADA` markers for pending, cross-references message catalog for coverage, and emits the JSON summary. This is purely counting and cross-referencing — zero semantic judgment needed.
- **Estimated token savings:** ~150-250 tokens per invocation (counting/aggregation work + JSON formatting).
- **Pre-pass potential:** No — post-pass aggregation.
- **Standalone value:** Medium — useful for CI pipelines that consume the JSON output.
- **Reuse across skills:** Medium — the pattern of "generate structured summary from markdown artifact" is common.

## Aggregate Savings

| Finding | Severity | Est. Token Savings | Type |
|---------|----------|-------------------|------|
| Prerequisite check | Low | ~80 | Pre-pass |
| US inventory extraction | Medium | ~300-800 | Pre-pass |
| Message catalog parsing | Medium | ~200-500 | Pre-pass |
| Coverage validation | Medium | ~400-700 | Post-pass |
| Technical jargon detection | Medium | ~150-300 | Post-pass |
| Headless JSON summary | Low | ~150-250 | Post-pass |

**Total estimated savings: ~1,280-2,630 tokens per invocation.**

The highest-impact opportunities are the US inventory extraction (Finding 2) and coverage validation (Finding 4). Together they account for roughly half the savings and would also improve deterministic reliability — the LLM occasionally misses a US or message during manual verification, while a script never will.

A recommended implementation order would be:
1. **Coverage validator + jargon checker** (Findings 4+5, can be one script) — immediate post-pass reliability gain
2. **US inventory extractor** (Finding 2) — reduces pre-pass token cost and feeds the coverage validator
3. **Message catalog parser** (Finding 3) — completes the pre-pass pipeline
4. **Prerequisite checker** (Finding 1) and **JSON summary generator** (Finding 6) — smaller wins, easy to implement
