# Script Opportunities Analysis — tjce-verify

**Skill:** `skills/tjce-verify/`
**Date:** 2026-04-16T15:41:45
**Analyzer:** ScriptHunter

---

## 1. Existing Scripts Inventory

| Script | Purpose | Quality | Test Coverage |
| ------ | ------- | ------- | ------------- |
| `scripts/check-build-artifacts.py` | File existence check for BUILD outputs | Excellent — pure determinism, JSON output, proper exit codes | Yes (`test_check-build-artifacts.py`) |
| `scripts/scan-secrets.py` | Regex-based secret detection in source code | Excellent — pattern matching only, skip-lists for fixtures/mocks | Yes (`test_scan-secrets.py`) |
| `scripts/validate-security.py` | OWASP pattern scanning (SQLi, CORS, auth) | Excellent — per-extension checks, proper severity tiers | Yes (`test_validate-security.py`) |
| `scripts/consolidate-results.py` | Aggregate layer results into Go/No-Go verdict | Excellent — coverage extraction, defect counting, verdict logic | Yes (`test_consolidate-results.py`) |

**Assessment:** The existing script suite is well-designed. All four follow a consistent contract: JSON output, exit code discipline (0=pass, 1=fail), `--output`/`--verbose` flags, unit tests. This is a mature foundation. The analysis below focuses exclusively on deterministic work that remains embedded in the LLM prompts.

---

## 2. Findings

### Finding 1 — Coverage Parsing from Cycle Report (Stage 2)

- **Severity:** Medium
- **File:** `references/pre-check-and-automated.md`, lines 43-44
- **Current work in prompt:** "Read the generated test cycle report from `{output_folder}/reports/`" and "Parse coverage percentage from the cycle report"
- **Determinism test:** Coverage percentage is a number embedded in structured text. Regex extraction is deterministic. `consolidate-results.py` already does this same extraction (lines 20-30 in the script) for the layer1 report. The LLM is being asked to parse a number out of a markdown file — identical input always produces identical output.
- **Script alternative:** Extend `consolidate-results.py` with a standalone `extract-coverage` subcommand, or create a small `parse-cycle-report.py` script that extracts coverage %, test counts (total/passed/failed/skipped), and returns JSON. The LLM then only needs to decide pass/block based on the structured data.
- **Estimated LLM tax:** ~200-300 tokens per invocation (reading markdown, locating the coverage line, extracting the number, structuring the result)
- **Note:** The consolidation script already has `extract_coverage()` — this is partially duplicated work. The LLM is doing at Stage 2 what the script later does at Stage 5.

### Finding 2 — Test Cycle Number Discovery (Stage 3)

- **Severity:** Low
- **File:** `references/functional-and-security.md`, line 19
- **Current work in prompt:** "Determine the next cycle number by scanning existing `{output_folder}/reports/test-cycle-*.md` files"
- **Determinism test:** Glob for files matching a pattern, parse numeric suffix, increment. Pure filesystem operation. Given identical files, always identical result. Trivially unit-testable.
- **Script alternative:** A small utility `next-cycle-number.py {output_folder}` that outputs the next integer. Or add it as a flag to an existing script. One-liner in Python: `max([int(re.search(r'(\d+)', f.stem).group()) for f in Path(reports).glob('test-cycle-*.md')], default=0) + 1`.
- **Estimated LLM tax:** ~100-150 tokens per invocation (listing files, pattern matching, arithmetic)
- **Note:** Low severity because the token cost is small, but it is unambiguously deterministic and creates a fragility — the LLM might miscalculate cycle numbers under edge cases (no prior cycles, gaps in numbering).

### Finding 3 — Cycle Report Completeness Validation (Stage 3)

- **Severity:** Medium
- **File:** `references/functional-and-security.md`, lines 24-27
- **Current work in prompt:** "Verify the cycle report contains: Execution results for all test cases from `test-cases.md`, Defects classified by TJCE severity with evidence, Go/No-Go recommendation"
- **Determinism test:** This is a hybrid. Checking structural presence of sections (headers, severity columns, recommendation section) is deterministic. Verifying that ALL test cases from `test-cases.md` have corresponding results requires matching test case IDs/names — also deterministic if IDs are structured. However, judging whether the "evidence" is adequate requires interpretation.
- **Script alternative:** A `validate-cycle-report.py` that: (a) extracts test case IDs from `test-cases.md`, (b) extracts executed test case IDs from `test-cycle-N.md`, (c) computes the diff (missing/extra), (d) checks for presence of severity column, (e) checks for Go/No-Go section. Return JSON with structural pass/fail and list of unmatched test cases. Leave evidence quality assessment to LLM.
- **Estimated LLM tax:** ~300-500 tokens per invocation (cross-referencing two documents, checking structural elements, comparing lists)
- **Note:** The structural checks account for ~70% of the work and are fully deterministic. Only evidence quality assessment requires LLM judgment.

### Finding 4 — Security Report Markdown Assembly (Stage 4)

- **Severity:** High
- **File:** `references/functional-and-security.md`, lines 44-48
- **Current work in prompt:** "Write `{output_folder}/reports/security-report.md` combining findings from both scans: Findings organized by severity (critical/high/medium/low), File path and line number for each finding, Category (secrets, injection, CORS, auth, input validation)"
- **Determinism test:** Both scan scripts (`scan-secrets.py` and `validate-security.py`) output structured JSON. Combining two JSON outputs into a sorted markdown report is a pure transformation — identical JSON always produces identical markdown. No interpretation needed. This is the highest-value script opportunity because the LLM is essentially being used as a JSON-to-Markdown template engine.
- **Script alternative:** A `format-security-report.py` that: (a) reads JSON output from both scan scripts, (b) merges findings, (c) sorts by severity, (d) renders to markdown using a template. Input: two JSON files. Output: `security-report.md`. The two scan scripts already produce all the data fields the report needs (severity, category, file, line, issue, fix, evidence).
- **Estimated LLM tax:** ~500-800 tokens per invocation (reading two JSON results, sorting, formatting markdown tables, organizing by severity category)
- **Note:** This is the single largest deterministic token sink remaining. The LLM adds zero judgment value — it is acting as `jq` + a markdown template.

### Finding 5 — Verify Summary Markdown Formatting (Stage 5)

- **Severity:** High
- **File:** `references/consolidation-and-gate.md`, lines 25-32 and line 38
- **Current work in prompt:** "Use the script's JSON output to generate the markdown summary. The script provides the verdict and all metrics — the workflow formats the human-readable report." The output must contain: Executive summary with Go/No-Go verdict, Per-layer results overview, Consolidated findings by severity, Coverage metrics and threshold status, Risk assessment, Specific conditions (if GO COM RESSALVAS).
- **Determinism test:** The prompt itself acknowledges this is a data-to-markdown transformation ("The script provides the verdict and all metrics — the workflow formats the human-readable report"). Given the same JSON from `consolidate-results.py`, the markdown structure is entirely determined. Only "Risk assessment" has a subjective element, but even that is derivable from the severity counts and verdict. The GO COM RESSALVAS conditions are enumerated in the JSON findings.
- **Script alternative:** Extend `consolidate-results.py` with a `--format markdown` flag that renders `verify-summary.md` directly from the computed data. The template is fixed: heading, verdict badge, metrics table, findings table, conditions list. Alternatively, a separate `render-verify-summary.py` that takes the consolidation JSON and outputs markdown.
- **Estimated LLM tax:** ~500-700 tokens per invocation (reading JSON, structuring markdown with headings, tables, bullet points, formatting coverage/defect/security sections)
- **Note:** This is the second largest deterministic token sink. Combined with Finding 4, these two formatting tasks account for over 1000 tokens of pure template rendering per verification run.

### Finding 6 — Layer 1 Report Markdown Formatting (Stage 2)

- **Severity:** Medium
- **File:** `references/pre-check-and-automated.md`, lines 51-56
- **Current work in prompt:** "Write `{output_folder}/reports/verify-layer1-automated.md` with: Timestamp and execution environment, Test execution summary (total, passed, failed, skipped), Coverage percentage and per-module breakdown, Pass/Block status with reasoning, If blocked: specific gaps and recommended actions"
- **Determinism test:** Timestamp, test counts, coverage %, and pass/block status are all structured data from `tjce-agent-qa verify` output. Formatting them into markdown is deterministic. The "reasoning" for pass is fixed ("Coverage meets threshold"). For block, the "specific gaps" are the module names below threshold — also structured data. Only "recommended actions" has a slight interpretive element, but standard templates cover 95% of cases (e.g., "Add tests for module X to reach Y% coverage").
- **Script alternative:** A `format-layer1-report.py` that takes the test execution JSON/output and renders the markdown report. Template-fill for ~90% of content; the LLM can optionally append interpretive notes.
- **Estimated LLM tax:** ~300-500 tokens per invocation (structuring timestamp, tables, status, gaps analysis)
- **Note:** Medium rather than high because some of the input (tjce-agent-qa output) may not be as cleanly structured as the security scan JSON, requiring minor parsing.

---

## 3. Aggregate Impact

| # | Finding | Severity | Tokens/invocation | Determinism % |
|---|---------|----------|-------------------|---------------|
| 1 | Coverage parsing from cycle report | Medium | 200-300 | 100% |
| 2 | Test cycle number discovery | Low | 100-150 | 100% |
| 3 | Cycle report completeness validation | Medium | 300-500 | ~70% |
| 4 | Security report markdown assembly | **High** | 500-800 | 100% |
| 5 | Verify summary markdown formatting | **High** | 500-700 | ~90% |
| 6 | Layer 1 report markdown formatting | Medium | 300-500 | ~90% |

**Total estimated LLM tax on deterministic work:** 1,900-2,950 tokens per full verification run.

**Priority ranking by ROI (savings vs. implementation effort):**

1. **Finding 4 — Security report assembly** (High / trivial implementation). Both input scripts already emit JSON. A 50-line Python script with string templates eliminates 500-800 tokens. Zero ambiguity.
2. **Finding 5 — Verify summary formatting** (High / trivial implementation). `consolidate-results.py` already computes everything. Adding `--format markdown` is a natural extension to an existing script.
3. **Finding 1 — Coverage parsing** (Medium / near-zero effort). `consolidate-results.py` already has `extract_coverage()`. Expose as CLI subcommand or standalone utility.
4. **Finding 3 — Cycle report validation** (Medium / moderate effort). Requires parsing test case IDs from two files. Worth scripting the structural checks; leave evidence quality to LLM.
5. **Finding 6 — Layer 1 report formatting** (Medium / moderate effort). Depends on how structured `tjce-agent-qa` output is.
6. **Finding 2 — Cycle number discovery** (Low / trivial effort). Small token savings but eliminates an edge-case fragility.

---

## 4. What Is Correctly Kept as Prompt

The following operations in the prompts **should remain as LLM work**:

- **Stage 6 — Human gate interaction** (interpreting PO decisions, capturing feedback, understanding AJUSTAR specifics)
- **Stage 2 — Invoking tjce-agent-qa and interpreting its unstructured output** (agent orchestration requires LLM flexibility)
- **Stage 3 — Judging evidence quality** in cycle reports (requires understanding whether evidence adequately supports a defect classification)
- **Stage 5 — Risk assessment narrative** (the ~10% of the summary that requires synthesizing qualitative judgment across layers)
- **Blocking decision communication** (explaining WHY something is blocked in natural language tailored to the user's context)

---

## 5. Recommendations

### Immediate (Findings 4, 5 — eliminate ~1,000-1,500 tokens)

Create two scripts:

1. **`scripts/format-security-report.py`** — Reads JSON from `scan-secrets.py` and `validate-security.py`, merges, sorts by severity, outputs `security-report.md`. Input: two JSON file paths. Output: markdown file.

2. **Extend `scripts/consolidate-results.py` with `--format markdown`** — When flag is present, also write `verify-summary.md` alongside the JSON. The template is fixed: verdict heading, metrics table, findings list, conditions (if GO COM RESSALVAS).

### Short-term (Findings 1, 2, 3 — eliminate ~600-950 tokens)

3. **`scripts/parse-cycle-report.py`** — Extracts coverage %, test counts, defect counts from a cycle report or layer1 report. Returns JSON. Reuse `extract_coverage()` and `count_defects_by_severity()` from `consolidate-results.py` (consider refactoring into a shared module).

4. **`scripts/validate-cycle-completeness.py`** — Cross-references test case IDs between `test-cases.md` and `test-cycle-N.md`. Returns JSON with matched/unmatched/coverage.

5. **Add cycle number resolution** to `parse-cycle-report.py` or as a small standalone utility.

### Architecture note

Consider extracting shared functions (`extract_coverage`, `count_defects_by_severity`, `count_security_findings`, severity counting) into a `scripts/lib/` module to avoid duplication across scripts. The existing scripts already share patterns (SKIP_DIRS, JSON output contract, exit code discipline) that would benefit from a small shared library.
