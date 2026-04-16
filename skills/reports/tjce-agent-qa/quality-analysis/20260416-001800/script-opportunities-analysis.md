# Script Opportunities Analysis — tjce-agent-qa

**Analyst:** ScriptHunter  
**Date:** 2026-04-16  
**Subject:** `skills/tjce-agent-qa/` — SKILL.md + build-capability.md + verify-capability.md  
**Verdict:** 6 script opportunities identified across BUILD and VERIFY capabilities

---

## Scoring Key

| LLM Tax | Tokens per invocation | Meaning |
|---------|----------------------|---------|
| High | 500+ | LLM is doing arithmetic or lookup; provably wasteful |
| Medium | 100–500 | LLM is parsing structured text it did not generate |
| Low | <100 | LLM overhead is small but still non-zero on deterministic work |

---

## Already Scripted — Correct Placement

### `scripts/parse-coverage.py`

**Status: Good intelligence placement.**

Coverage parsing (pytest-cov term-missing format, Jest --coverage table format) is deterministic regex extraction. The script correctly handles:
- Per-file coverage breakdown
- Total coverage calculation (with fallback when no TOTAL line)
- Threshold comparison with exit codes 0/1/2
- `--json` flag for machine-readable output downstream

Both capabilities already invoke this script after running the test suites. No action required here.

---

## Opportunities

### OPP-001 — RN List Extraction from `business-rules.md`

**Location:** `build-capability.md`, Section 1 — Test Cases Generation  
**LLM Tax: High (500–800 tokens)**

**What the LLM does today:** Reads `business-rules.md` in full and mentally enumerates all RN identifiers before beginning test case generation.

**Why it is deterministic:** Business rules in TJCE artifacts follow a fixed pattern (`RN-NNN` identifiers in a markdown table or heading structure). Extracting them is a regex scan — zero ambiguity.

**Script:** `scripts/extract-rn-list.py`
```
Usage: python3 extract-rn-list.py {output_folder}/requirements/business-rules.md
Output (stdout, one per line): RN-001, RN-002, ...
Exit 1 if file not found or no RN found.
```

**Downstream value:** The LLM receives a compact enumerated list as its context preamble instead of the full file, reducing prompt size and eliminating any risk of the LLM silently skipping an RN.

---

### OPP-002 — RN → CT Traceability Matrix Validation

**Location:** `build-capability.md`, Section 1 — "After generating, verify this cross-reference"  
**LLM Tax: High (600–1000 tokens)**

**What the LLM does today:** After writing `test-cases.md`, re-reads it to mentally cross-reference every `RN-NNN` against the RN list and identify uncovered rules.

**Why it is deterministic:** `test-cases.md` has a fixed schema (table with an `RN` column). Extracting the set of RNs that appear in that column and diffing against the extracted RN list (OPP-001) is pure set arithmetic.

**Script:** `scripts/validate-traceability.py`
```
Usage: python3 validate-traceability.py \
    --rn-source {output_folder}/requirements/business-rules.md \
    --test-cases {output_folder}/tests/test-cases.md
Output: JSON { "covered": [...], "uncovered": [...], "pass": bool }
Exit 1 if uncovered RNs exist.
```

**This is the most impactful opportunity.** Traceability is a hard correctness check — a required invariant, not a judgment call. Delegating it to an LLM introduces non-determinism (hallucination risk on "all RNs are covered") on work that a 20-line script handles with 100% accuracy.

---

### OPP-003 — Test Cycle Number Auto-Increment

**Location:** `verify-capability.md`, Section — Test Cycle Documentation  
**LLM Tax: Medium (100–200 tokens)**

**What the LLM does today:** Scans `{output_folder}/reports/test-cycle-*.md` to determine the next cycle number (N+1).

**Why it is deterministic:** File glob + max integer extraction is a two-liner.

**Script:** `scripts/next-cycle-number.py`
```
Usage: python3 next-cycle-number.py {output_folder}/reports/
Output (stdout): integer, e.g. "3"
Exit 0 always (returns 1 if no cycles exist yet).
```

**Risk of not scripting:** The LLM could miscalculate N if cycle files are non-contiguous (e.g., `test-cycle-1.md`, `test-cycle-3.md` after a deletion), producing a duplicate or skipped cycle number that corrupts the cycle history.

---

### OPP-004 — `test-cases.md` Schema Validation

**Location:** `build-capability.md`, Section 1 — implied post-write validation  
**LLM Tax: Medium (200–400 tokens)**

**What the LLM does today:** Implicitly responsible for ensuring the generated `test-cases.md` contains all required columns (ID, Titulo, RN, Pre-condicao, Passos, Resultado Esperado, Tipo). There is no explicit validation step, so schema drift is silent.

**Why it is deterministic:** Required column headers are fixed. Checking that every row in the markdown table has exactly 7 non-empty columns is regex + row-counting.

**Script:** `scripts/validate-test-cases-schema.py`
```
Usage: python3 validate-test-cases-schema.py {output_folder}/tests/test-cases.md
Output: JSON { "rows": N, "missing_columns": [...], "empty_cells": [...], "pass": bool }
Exit 1 on schema violation.
```

**Secondary benefit:** Catches cases where the LLM collapses two columns or omits "Pre-condicao" silently — a real failure mode under context pressure.

---

### OPP-005 — Test Result Tallying (pass/fail/skip counts)

**Location:** `verify-capability.md`, Section — Results summary in cycle report  
**LLM Tax: Medium (150–300 tokens)**

**What the LLM does today:** Reads raw pytest/Jest output and tallies "total tests, passed, failed, skipped" numbers to write the Results summary block of the cycle report.

**Why it is deterministic:** pytest prints `X passed, Y failed, Z warnings` on the final summary line. Jest prints `Tests: X passed, Y failed, Z total`. Both are single-line regex extractions — already adjacent to the work `parse-coverage.py` does.

**Recommendation:** Extend `parse-coverage.py` with a `--test-counts` mode, or create `scripts/parse-test-results.py` that extracts pass/fail/skip counts alongside coverage. The script already reads the same output stream.

**Script extension:** `parse-coverage.py --test-counts`
```
Adds to JSON output: { "tests": { "passed": N, "failed": N, "skipped": N, "total": N } }
```

---

### OPP-006 — Prerequisites Artifact Check

**Location:** `SKILL.md`, Section — Prerequisite Check  
**LLM Tax: Low (50–100 tokens per invocation)**

**What the LLM does today:** Checks existence of three fixed file paths before any capability runs:
- `{output_folder}/requirements/user-stories.md`
- `{output_folder}/requirements/business-rules.md`
- `{output_folder}/requirements/messages.md`

**Why it is deterministic:** File existence check. Three `Path.exists()` calls.

**Script:** `scripts/check-prerequisites.py`
```
Usage: python3 check-prerequisites.py {output_folder}
Output: JSON { "missing": [...], "all_present": bool }
Exit 1 if any missing.
```

**Note:** LLM Tax is Low here and the risk of hallucination is also low (a missing file produces an obvious error). This is a nice-to-have rather than a priority fix — schedule after OPP-001 through OPP-005.

---

## Priority Order

| Priority | OPP | Reason |
|----------|-----|--------|
| 1 | OPP-002 | Correctness invariant — hallucination risk on traceability claim is unacceptable |
| 2 | OPP-001 | Prerequisite for OPP-002; also reduces context pressure on test generation |
| 3 | OPP-004 | Silent schema drift causes downstream failures in VERIFY |
| 4 | OPP-005 | Extends existing script; low effort, eliminates arithmetic errors in cycle reports |
| 5 | OPP-003 | Low risk today, but cycle number corruption is hard to repair retroactively |
| 6 | OPP-006 | Nice-to-have; current LLM behavior is already reliable here |

---

## Determinism Test — Full Operation Inventory

| Operation | Deterministic? | Current handling | Verdict |
|-----------|---------------|-----------------|---------|
| Parse pytest-cov output → metrics | Yes | `parse-coverage.py` | Already scripted |
| Parse Jest --coverage output → metrics | Yes | `parse-coverage.py` | Already scripted |
| Coverage threshold comparison | Yes | `parse-coverage.py` | Already scripted |
| Extract RN identifiers from business-rules.md | Yes | LLM reads full file | OPP-001 |
| Cross-reference RN list vs CT table | Yes | LLM mental check | OPP-002 (highest priority) |
| Scan test-cycle-*.md for next cycle N | Yes | LLM scans files | OPP-003 |
| Validate test-cases.md column schema | Yes | Not validated | OPP-004 |
| Tally pass/fail/skip from test output | Yes | LLM reads output | OPP-005 |
| Check prerequisite artifact existence | Yes | LLM checks paths | OPP-006 |
| Detect project stack (pytest vs Jest) | Mostly | LLM scans codebase | Acceptable — judgment involved |
| Derive test cases from RNs | No | LLM — correct | Core LLM value |
| Classify defect severity | No | LLM — correct | Core LLM value |
| Write code review findings | No | LLM — correct | Core LLM value |
| Go/No-Go recommendation | Partly | LLM — acceptable | Threshold check scriptable (OPP-005 feeds this) |
| Generate unit test code | No | LLM — correct | Core LLM value |

---

## Summary

The existing `parse-coverage.py` demonstrates correct intelligence placement — deterministic regex work extracted into a tested script with exit codes. That pattern should be applied to six more operations. The two highest-priority opportunities (OPP-001 + OPP-002) together eliminate the risk that the LLM silently claims traceability compliance without actually verifying it — a failure mode that directly violates the skill's stated invariant: "Todo caso de teste vinculado a pelo menos uma Regra de Negocio."
