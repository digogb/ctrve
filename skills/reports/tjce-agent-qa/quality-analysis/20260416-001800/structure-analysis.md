---
report: structure-analysis
analyzer: StructureBot
agent: tjce-agent-qa
timestamp: 2026-04-16T00:18:00+00:00
prepass_ref: structure-capabilities-prepass.json
---

# Structure Analysis — tjce-agent-qa

## Pre-pass Findings (as-is)

Source: `structure-capabilities-prepass.json` | Scanner v1.0.0 | Status: **warning**

### Frontmatter

| Field | Value | Status |
|-------|-------|--------|
| `name` | `tjce-agent-qa` | OK |
| `description` | Present — 172 chars | OK |
| `is_memory_agent` | `false` | OK (stateless) |

### Sections Detected

| Level | Title | Line |
|-------|-------|------|
| H2 | Overview | 8 |
| H2 | Identity | 16 |
| H2 | Communication Style | 20 |
| H2 | Principles | 28 |
| H2 | On Activation | 34 |
| H3 | Prerequisite Check | 43 |
| H3 | Capability Routing | 53 |

All expected structural sections are present. No orphaned or missing sections detected.

### Capability Files

| File | Config Header | Progression | Issues |
|------|--------------|-------------|--------|
| `build-capability.md` | YES | YES | None |
| `verify-capability.md` | YES | NO | **HIGH** — No progression condition keywords found (line 97) |

### Pre-pass Issues Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| High | 1 |
| Medium | 0 |
| Low | 0 |

**High — verify-capability.md line 97:** The capability file has no progression condition keywords. The Headless Mode section at line 94–96 provides a headless exit summary but contains no conditional branching keywords (e.g., `if`, `when`, `only if`, `until`) to guide the LLM through decision points in verify flow execution. The build-capability.md's headless section does include a conditional ("If coverage < 80%, write the report with the blocking finding but continue") — verify is missing equivalent progression logic.

---

## Judgment-Based Checks

### 1. Description Quality

**Score: PASS**

```
Analista de Qualidade do TJCE para testes e code review. Use when the user asks to
generate tests, run test cycles, review code, check coverage, or classify defects
for TJCE projects.
```

- Uses action verbs: "generate", "run", "review", "check", "classify" — five distinct trigger verbs covering the full capability surface.
- Domain-scoped: "TJCE projects" prevents false activation on generic QA requests.
- Trigger phrasing ("Use when the user asks to...") is explicit and discriminating.
- Specific enough to distinguish from generic QA agents; would not trigger on unrelated prompts.

**No issues.**

---

### 2. Identity Effectiveness

**Score: PASS**

```
QA senior rigoroso e detalhista que trata cada defeito nao encontrado como falha
pessoal. Nao suaviza problemas, nao deixa passar "por enquanto", e nao aceita
cobertura abaixo de 80% como entregavel.
```

- Clear, single-sentence persona with a decisive professional stance.
- The metaphor ("trata cada defeito nao encontrado como falha pessoal") is vivid and will reliably shape LLM tone toward vigilance over diplomacy.
- Quantitative anchor (80%) embedded in identity prevents the LLM from drifting to softer coverage standards.
- Actionable: tells the LLM what to do (not soften findings, not pass below 80%) rather than just what to be.

**No issues.**

---

### 3. Communication Style Quality

**Score: PASS**

The section provides four concrete, actionable directives:

1. Language and register: "Portugues formal, vocabulario tecnico de QA e desenvolvimento"
2. Negative example pair: `"A funcao X nao tem teste para o caminho de excecao da RN-003" — nunca "talvez seria bom considerar testar..."` — this before/after contrast is the strongest possible style anchor; the LLM receives both the target form and the anti-pattern.
3. Reporting format: "Reporta problemas com severidade, localizacao exata e evidencia" — three mandatory fields per finding.
4. Blocking behaviour: explicit protocol for sub-80% coverage (declare, list gaps, stop).
5. Positive acknowledgement: brief recognition for good work prevents the persona from reading as purely adversarial.

The negative-example pattern is particularly effective and matches the persona well.

**No issues.**

---

### 4. Principles Quality

**Score: PASS**

Three principles, each domain-specific and operational:

| Principle | Assessment |
|-----------|-----------|
| Rastreabilidade requisito-teste | Guiding — defines "orphan test" and explains *why* traceability matters (tests without RN linkage prove nothing). Not generic. |
| 80% e o minimo, nao o alvo | Guiding — reframes the threshold as a floor, not a goal. Includes specific action: identify uncovered modules/functions and suggest remediation. |
| Evidencia sobre opiniao | Guiding — establishes the epistemic standard for all outputs (observable facts over impressions). Provides the anti-pattern ("Nunca 'parece que pode ter um problema'"). |

No generic filler principles present (e.g., "be thorough", "communicate clearly"). All three are specific to TJCE QA practice and would meaningfully constrain LLM behaviour differently from a default.

**No issues.**

---

### 5. Over-specification of LLM Capabilities

**Score: PASS with minor note**

The agent appropriately branches on tool availability ("If Bash tool is available / NOT available") in both capability files — this is correct over-specification awareness. The agent does not claim to autonomously run code without the Bash tool.

**Minor note (Low):** `build-capability.md` section 2 references scanning the codebase to detect project stack ("Detect the project stack by scanning the codebase"). This implies filesystem read access, which is tool-dependent. The section does not include a fallback for when file-read tools are unavailable (contrast with how coverage commands correctly provide a no-Bash fallback). This is a low-severity gap — the user can always provide stack information manually, but the agent does not explicitly prompt for it in the no-tool path.

---

### 6. Logical Consistency

**Score: PASS with one note**

- The prerequisite check in SKILL.md (requirement artifacts must exist) is consistent with BUILD capability's step 1 (reads the same three files).
- VERIFY's prerequisite check is softer by design ("inform the user... but do not block") — this is an intentional and well-documented asymmetry, not an inconsistency.
- The GO/NO-GO criteria in VERIFY are internally consistent: any Alta severity or coverage <80% triggers NO-GO, matching the 80% floor declared in Principles.
- Config variable resolution is declared once in SKILL.md and referenced correctly in both capability files via the config note header.

**Inconsistency note (Low):** `verify-capability.md` line 92 writes the test plan to `{output_folder}/tests/test-plan.md`, but the section header above (line 85) describes updating `{output_folder}/reports/test-plan.md`. The path in the prose body (`reports/`) and the write instruction (`tests/`) differ. This will produce inconsistent artifact placement depending on which instruction the LLM follows.

---

### 7. Headless Mode Setup

**Score: PASS for BUILD / PARTIAL for VERIFY**

| Capability | Headless Declared | Behaviour Specified | Progression Logic |
|-----------|------------------|---------------------|-------------------|
| build-capability.md | YES (`--headless`/`-H`) | YES — four sequential steps, explicit coverage-gate override | YES — conditional on coverage result |
| verify-capability.md | YES (`--headless`/`-H`) | YES — execute, report, classify, exit with structured summary | NO — pre-pass finding confirmed; no conditional branching |

SKILL.md correctly declares `--headless` / `-H` and routes to capabilities. The `--headless build` and `--headless verify` routing is explicit in Capability Routing.

VERIFY headless exits with a structured summary but provides no LLM decision path for partial states (e.g., what to do if test files are absent in headless mode, or if the Bash tool is unavailable mid-run). BUILD handles its partial states explicitly; VERIFY does not.

---

### 8. Stateless Agent Checks (is_memory_agent: false)

**Score: PASS**

- No memory paths declared — confirmed by pre-pass (`memory_paths: []`).
- Session state (config variables) is loaded fresh at activation from config files, not from prior session memory. This is the correct stateless pattern.
- The agent does not reference any cross-session state, stored context, or accumulated knowledge.
- Cycle numbering in VERIFY (auto-increment by scanning `test-cycle-*.md` files) derives state from filesystem artifacts, not from LLM memory — correct approach for a stateless agent.

**No issues.**

---

## Issue Register

| ID | File | Severity | Category | Description |
|----|------|----------|----------|-------------|
| SA-001 | verify-capability.md | High | progression | No progression condition keywords in headless mode section (pre-pass confirmed, line 97). No conditional branches for partial-state handling (Bash unavailable, test files missing) during headless execution. |
| SA-002 | verify-capability.md | Low | consistency | Path conflict: section prose references `{output_folder}/reports/test-plan.md` (line 86) but write instruction uses `{output_folder}/tests/test-plan.md` (line 92). |
| SA-003 | build-capability.md | Low | over-specification | Stack detection via codebase scan (section 2) has no fallback when file-read tools are unavailable. BUILD correctly handles no-Bash for coverage; should apply same pattern to stack detection. |

---

## Summary

| Dimension | Result |
|-----------|--------|
| Frontmatter | PASS |
| Sections | PASS |
| Cross-references | PASS |
| Template artifacts | PASS |
| Description quality | PASS |
| Identity effectiveness | PASS |
| Communication style | PASS |
| Principles quality | PASS |
| LLM capability over-specification | PASS (minor SA-003) |
| Logical consistency | PASS (minor SA-002) |
| Headless mode — BUILD | PASS |
| Headless mode — VERIFY | PARTIAL (SA-001) |
| Stateless agent checks | PASS |

**Total issues:** 3 (1 High, 0 Medium, 2 Low)

The agent is well-constructed. Its identity, communication style, and principles are concrete, domain-specific, and would reliably shape LLM behaviour toward rigorous QA practice. The single High finding (SA-001) is contained to VERIFY's headless path and does not affect interactive operation. The two Low findings are straightforward corrections. No Critical issues found.
