# Script Opportunities Analysis — tjce-requirements skill

**Date:** 2026-04-15  
**Analyst:** ScriptHunter  
**Target:** `skills/tjce-requirements/`  
**Scope:** Identify deterministic operations currently delegated to LLM prompts

---

## Executive Summary

The `tjce-requirements` skill delegates 11 clearly deterministic operations to the LLM. These range from ID validation and cross-reference integrity checks to file-system scanning and token counting. Collectively, they impose an estimated **1,800–3,200 tokens of LLM Tax per invocation** on work that could be handled by scripts with zero token cost, lower latency, and guaranteed correctness.

---

## Findings

### SO-001 — Input File Scanner (Pre-processing)

**Source:** `SKILL.md` — "On Activation > Input Detection" (lines 49–54)

**Current behavior:** The LLM is instructed to scan `{planning_artifacts}` for PRD/brief files and determine whether a structured input exists.

**Determinism test:** PASS. Given a directory path, the set of files present is a fixed fact. The decision tree (file found / not found) is purely conditional on filesystem state.

**Script action:**
- Enumerate files matching `*.md`, `*.txt`, `*.pdf` under `{planning_artifacts}`
- Return structured result: `{ found: true, path: "...", type: "prd|brief|unknown" }` or `{ found: false }`
- LLM receives pre-resolved input descriptor, not a scan instruction

**LLM Tax eliminated:** ~150 tokens (scan instruction + directory traversal reasoning + decision output)

---

### SO-002 — Config Loader (Pre-processing)

**Source:** `SKILL.md` — "On Activation" (lines 38–45)

**Current behavior:** The LLM is instructed to load `_bmad/config.yaml` and `_bmad/config.user.yaml`, merge them, and resolve all variables before proceeding.

**Determinism test:** PASS. YAML parsing and key lookup are fully deterministic. Merge strategy (user overrides base) is fixed. Default values are explicitly defined.

**Script action:**
- Parse both YAML files if present
- Apply merge: user config overrides base, defaults fill gaps
- Inject resolved variables into the LLM context as a flat key-value block
- LLM never reads raw YAML files

**LLM Tax eliminated:** ~200 tokens (load instructions + file-reading + variable resolution reasoning)

---

### SO-003 — ID Sequential Validator (Post-processing)

**Source:** `generate-requirements.md` — Self-Validation checklist (line 72): "IDs are sequential and consistent (US-001, RN-001, MSG-001)"

**Current behavior:** The LLM is instructed to verify that all IDs across three artifact files are sequential, zero-padded to three digits, and use the correct prefix.

**Determinism test:** PASS. Given a set of IDs, sequential verification is a pure string/integer operation.

**Script action:**
- Extract all IDs from each artifact using regex: `US-\d{3}`, `RN-\d{3}`, `MSG-\d{3}`
- Verify: no gaps, no duplicates, starts at 001, zero-padded
- Return pass/fail with exact violations listed (e.g., "US-004 missing, gap after US-003")

**LLM Tax eliminated:** ~300 tokens (self-check instruction + LLM scanning all four files + reasoning about sequences)

---

### SO-004 — Cross-Reference Integrity Check: RN → US (Post-processing)

**Source:** `generate-requirements.md` — Traceability Constraints (lines 22–29) and Self-Validation (lines 64–65)

**Current behavior:** The LLM verifies that every RN in `business-rules.md` references at least one US-ID that actually exists in `user-stories.md`.

**Determinism test:** PASS. Set membership check — RN.Estoria column values must be subsets of the US-ID universe.

**Script action:**
- Extract all US-IDs from `user-stories.md` → Set A
- Extract all RN rows from `business-rules.md`; for each row, parse the Estoria column → Set B
- Flag any ID in B not present in A
- Return: `{ valid: true }` or `{ violations: [{ rn: "RN-005", bad_refs: ["US-099"] }] }`

**LLM Tax eliminated:** ~400 tokens (reading both files + cross-reference reasoning across potentially large tables)

---

### SO-005 — Cross-Reference Integrity Check: MSG → RN (Post-processing)

**Source:** `generate-requirements.md` — Traceability Constraints (line 24) and Self-Validation (line 66)

**Current behavior:** The LLM verifies that every MSG in `messages.md` references at least one RN-ID that exists in `business-rules.md`.

**Determinism test:** PASS. Identical logic to SO-004 but for the MSG → RN link.

**Script action:**
- Extract all RN-IDs from `business-rules.md` → Set A
- Extract all MSG rows from `messages.md`; for each row, parse the Regra column → Set B
- Flag any ID in B not present in A
- Return violations with exact MSG codes and bad references

**LLM Tax eliminated:** ~350 tokens

---

### SO-006 — Message Type Coverage Checker (Post-processing)

**Source:** `generate-requirements.md` — Self-Validation (line 68); `artifact-templates.md` — messages.md conventions (lines 110–114)

**Current behavior:** The LLM verifies that the messages artifact contains at least one entry of each of the four required types: `erro`, `sucesso`, `validacao`, `confirmacao`.

**Determinism test:** PASS. Extract the Tipo column values; check that the four required strings appear at least once each.

**Script action:**
- Parse `messages.md` table, extract all values in the Tipo column
- Required set: `{"erro", "sucesso", "validacao", "confirmacao"}`
- Return: `{ covered: true }` or `{ missing: ["confirmacao"] }`
- Bonus: flag any Tipo value not in the allowed set (typo detection)

**LLM Tax eliminated:** ~150 tokens

---

### SO-007 — Empty/Placeholder Cell Detector (Post-processing)

**Source:** `generate-requirements.md` — Self-Validation (line 69): "No cell contains 'TODO', 'TBD', 'a definir', or is empty"

**Current behavior:** The LLM scans all four artifact files for placeholder strings and empty table cells.

**Determinism test:** PASS. String matching against a fixed vocabulary of forbidden patterns is a pure text operation.

**Script action:**
- Scan all markdown table cells in the four output files
- Match against forbidden patterns: `TODO`, `TBD`, `a definir`, `verificar posteriormente`, empty string, whitespace-only
- Return a structured list: `{ file, row_id, column, value }`

**LLM Tax eliminated:** ~250 tokens (instruction + full re-read of four files + table cell inspection)

---

### SO-008 — Traceability Coverage Counter (Post-processing / Output Summary)

**Source:** `generate-requirements.md` — Output Summary (lines 77–83): "Total: X User Stories, Y Business Rules, Z Messages"

**Current behavior:** The LLM counts artifacts and states coverage after generation — as part of its narrative output summary.

**Determinism test:** PASS. Counting rows in markdown tables is deterministic given the generated files.

**Script action:**
- Count: US rows, RN rows, MSG rows across the three artifact files
- Compute: % of US IDs covered by at least one RN; % of RN IDs covered by at least one MSG
- Inject counts as structured data so LLM only writes the summary prose, not the counting

**LLM Tax eliminated:** ~200 tokens (counting + arithmetic + re-stating what was already generated)

---

### SO-009 — Assumptions File Writer (Post-processing)

**Source:** `generate-requirements.md` — headless mode (lines 43–45): "Generate a `spec/requirements/assumptions.md` listing all assumptions"

**Current behavior:** The LLM is expected to scan its own output for `[ASSUMIDO]` tags and compile them into a separate assumptions file.

**Determinism test:** PASS. Regex scan for `[ASSUMIDO]` tags across the four generated files, with their surrounding line context, is deterministic.

**Script action:**
- After LLM writes the four artifacts, scan all files for lines containing `[ASSUMIDO]`
- Extract: file name, line number, full line text
- Generate `assumptions.md` from a fixed template, injecting the extracted items
- LLM never needs to "remember" which assumptions it made

**LLM Tax eliminated:** ~300 tokens (instruction to remember and re-enumerate all assumptions + writing the file)

---

### SO-010 — Output Directory Initializer (Pre-processing)

**Source:** `generate-requirements.md` — lines 12–17 (implicit in "Four complete markdown files at `{project-root}/spec/requirements/`")

**Current behavior:** The LLM is implicitly responsible for ensuring the output path exists before writing files. In practice, file-writing tools may create directories automatically, but the LLM has no mechanism to verify this and may produce write errors that consume tokens to diagnose.

**Determinism test:** PASS. Directory creation is idempotent and deterministic.

**Script action:**
- Pre-run: `mkdir -p {project-root}/spec/requirements/`
- Verify write permissions
- Return: `{ ready: true, path: "..." }` before LLM begins generation

**LLM Tax eliminated:** ~50 tokens (implicit assumption handling, error recovery if path missing)

---

### SO-011 — N/A Exception Justification Validator (Post-processing)

**Source:** `artifact-templates.md` — business-rules.md conventions (line 91): "Coluna Excecao: nunca vazia. Se nao ha excecao, usar 'N/A — {motivo breve}'"

**Current behavior:** The LLM's self-validation must verify that no Excecao cell is empty, and that every cell containing "N/A" is followed by a dash and a brief justification — not just bare "N/A".

**Determinism test:** PASS. Pattern matching: cell must either be non-empty prose or match `N/A — .+` (at least one character of justification after the dash).

**Script action:**
- Parse the Excecao column in `business-rules.md`
- Flag: empty cells, "N/A" without `—`, "N/A — " with nothing after the dash
- Return violations: `{ rn: "RN-003", excecao_value: "N/A", issue: "missing_justification" }`

**LLM Tax eliminated:** ~150 tokens

---

## Prioritization

| Priority | ID     | Operation                              | LLM Tax (tokens) | Effort    | Impact      |
|----------|--------|----------------------------------------|------------------|-----------|-------------|
| P0       | SO-004 | Cross-ref: RN → US                     | ~400             | Low       | Correctness |
| P0       | SO-005 | Cross-ref: MSG → RN                    | ~350             | Low       | Correctness |
| P0       | SO-003 | ID sequential validator                | ~300             | Low       | Correctness |
| P0       | SO-009 | Assumptions file writer                | ~300             | Medium    | Reliability |
| P1       | SO-007 | Empty/placeholder detector             | ~250             | Low       | Quality     |
| P1       | SO-002 | Config loader                          | ~200             | Medium    | Reliability |
| P1       | SO-008 | Traceability counter                   | ~200             | Low       | Quality     |
| P2       | SO-001 | Input file scanner                     | ~150             | Low       | Reliability |
| P2       | SO-006 | Message type coverage                  | ~150             | Low       | Correctness |
| P2       | SO-011 | N/A justification validator            | ~150             | Low       | Quality     |
| P3       | SO-010 | Output directory initializer           | ~50              | Very Low  | Reliability |

**Total LLM Tax across all findings:** ~2,250–3,200 tokens/invocation  
**Immediate wins (P0, single-pass regex scripts):** SO-003, SO-004, SO-005 — ~1,050 tokens, implementable in < 1 hour combined

---

## Implementation Notes

### Recommended Script Architecture

All scripts should be stateless functions with a shared signature:

```
validate_<concern>(artifacts_dir: str) -> ValidationResult
  ValidationResult: { valid: bool, violations: list[Violation] }
  Violation: { artifact, entity_id, field, value, issue }
```

Pre-processing scripts (SO-001, SO-002, SO-010) return structured context injected before the LLM system prompt. Post-processing scripts (SO-003 through SO-009, SO-011) run after the LLM writes files and block output delivery until all checks pass or violations are explicitly surfaced.

### Recommended Integration Point

Add a `scripts/` directory under `skills/tjce-requirements/` with:

```
scripts/
  pre/
    scan-input.sh        # SO-001
    load-config.py       # SO-002
    init-output-dir.sh   # SO-010
  post/
    validate-ids.py      # SO-003
    check-rn-us-refs.py  # SO-004
    check-msg-rn-refs.py # SO-005
    check-msg-types.py   # SO-006
    detect-placeholders.py # SO-007
    count-coverage.py    # SO-008
    extract-assumptions.py # SO-009
    validate-na-excecao.py # SO-011
```

SKILL.md would invoke pre-scripts before loading `generate-requirements.md`, and post-scripts before presenting the output summary.

---

## What Should Remain LLM Work

The following operations from the prompt are **not** script candidates because they are genuinely non-deterministic or require semantic understanding:

- Interpreting a PRD to identify functional areas and actors
- Deriving business rules from narrative requirements
- Judging whether a user story has "enough" acceptance criteria
- Assessing whether a rule's Condition + Action combination is specific enough to yield a test
- Conducting the structured interview and deciding when it is complete
- Flagging ambiguities in source documents
- Producing the narrative prose in product-vision.md
