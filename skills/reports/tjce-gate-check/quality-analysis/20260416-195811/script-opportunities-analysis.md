# Script Opportunities Analysis — tjce-gate-check

**Skill:** `skills/tjce-gate-check/`
**Date:** 2026-04-16T19:58:11
**Analyzer:** ScriptHunter

---

## 1. Existing Scripts Inventory

| Script | Purpose | Quality | Test Coverage |
| ------ | ------- | ------- | ------------- |
| `scripts/check-artifacts-exist.py` | Layer 1: Check that all required SPEC artifacts exist and are non-empty. Supports conditional artifacts (data-model, ux) via flags. | Excellent — proper JSON output, exit codes, `--output`/`--verbose` flags, categorized findings with severity/fix | Yes (`test_check-artifacts-exist.py`) |
| `scripts/validate-cross-references.py` | Layer 2: Validate cross-references between SPEC artifacts (US, RN, MSG, CT IDs). Detects orphan IDs and missing linkages. | Excellent — regex-based ID extraction, context-aware linkage validation, defined vs. referenced ID tracking, JSON output | Yes (`test_validate-cross-references.py`) |
| `scripts/check-placeholders.py` | Layer 3 (partial): Detect placeholders (TODO, TBD, PREENCHER, etc.), empty sections, user story format, RN column structure, message type coverage. | Excellent — multi-pattern scanning, structural checks for US/RN/MSG formats, JSON output with line-level locations | Yes (`test_check-placeholders.py`) |
| `scripts/calculate-gate-score.py` | Weighted gate score calculation from all layer findings. Produces final verdict with PASS/FAIL determination. | Excellent — weighted scoring (40/30/30), severity deduction model, complementary decision recording (task_type, manual, data_model, apf_estimate), JSON verdict | Yes (`test_calculate-gate-score.py`) |

**Assessment:** This skill has the strongest script coverage of any skill analyzed so far. The four scripts cover Layers 1-3 (completeness, cross-references, placeholders/structural quality) and the scoring engine (Step 5) completely. All scripts follow a consistent contract (JSON output, exit codes, `--output`/`--verbose` flags) and have unit tests. The LLM is correctly limited to two roles: quality assessment of test case semantics (Step 4) and narrative report generation (Step 6). The remaining opportunities are narrow and focus on pre-processing/post-processing that can reduce the LLM's burden in those two remaining steps.

---

## 2. Findings

### Finding 1 — Test Case Structural Pre-Analysis (Step 4 pre-pass)

- **Severity:** Medium
- **File:** `SKILL.md`, line 55
- **Current work in prompt:** "Read the test cases file (`{output_folder}/tests/test-cases.md`). Assess whether each test case has a clear, verifiable expected result. Produce a `quality-findings.json` in the reports directory with findings in the standard format (severity, category, location, issue, fix)."
- **Determinism test:** Step 4 currently sends the entire test cases file to the LLM for quality assessment. While semantic judgment ("is this expected result truly verifiable?") requires the LLM, several structural preconditions are fully deterministic: (a) does each CT-NNN block have an "expected result" / "resultado esperado" section, (b) is that section non-empty, (c) does each CT-NNN reference at least one RN or US, (d) does each CT-NNN have preconditions/steps/postconditions sections. A pre-pass script can extract these structural signals and flag obvious failures, leaving the LLM to focus only on the semantic quality of non-trivially present expected results. This reduces the LLM's workload from "find structural gaps + assess quality" to "assess quality only on pre-validated cases."
- **Script alternative:** A `pre-analyze-test-cases.py` that: (a) parses test-cases.md into individual CT blocks using heading patterns, (b) checks each CT block for required sections (preconditions, steps, expected result), (c) checks that expected result sections are non-empty and have minimum content (not just a single word), (d) checks each CT references at least one ID (RN or US), (e) outputs JSON with per-CT structural findings and a filtered list of CTs that passed structural checks (for the LLM to assess semantically). The LLM then reads only the pre-analysis JSON + the structurally-valid CTs instead of re-parsing the entire file.
- **Estimated LLM tax:** ~400-800 tokens per invocation (parsing markdown structure, identifying section boundaries, checking for empty/missing sections across all CTs, then also doing the semantic work). The structural portion is ~200-400 tokens that a script would eliminate.
- **Note:** Medium severity because Step 4 is the primary remaining LLM task in this skill, and a pre-pass would both reduce tokens and improve correctness. The LLM might overlook a missing "resultado esperado" section buried in a long test cases file, but a regex parser will not miss it.

### Finding 2 — Report Generation from Template (Step 6 post-processing)

- **Severity:** Medium
- **File:** `SKILL.md`, lines 63-67
- **Current work in prompt:** "Generate `{output_folder}/reports/gate-check-report.md` from the verdict data. Include per-layer breakdown, all findings, and remediation guidance. For items below threshold, suggest which TJCE agent to invoke."
- **Determinism test:** The report contains two distinct components: (a) a structured data section (score tables, per-layer breakdowns, findings lists, agent mapping) that is entirely derivable from verdict.json and the findings JSONs, and (b) a narrative remediation section where the LLM adds contextual guidance. Component (a) is 100% deterministic — the layer scores, finding counts, severity distributions, and agent-to-fix mappings are all present in the JSON files. The LLM is spending tokens formatting structured data into markdown tables, which a script can do faster and with consistent formatting.
- **Script alternative:** A `generate-report-skeleton.py` that reads `gate-check-verdict.json` plus all `*-findings.json` files and produces a markdown skeleton with: (a) header with score, status, timestamp, (b) per-layer score table, (c) all findings formatted as a findings table with severity/category/location/issue/fix columns, (d) agent remediation mapping (e.g., "completeness" -> "tjce-agent-requirements", "cross-reference" -> relevant agent), (e) placeholder markers for LLM narrative sections (`<!-- LLM: Add remediation narrative here -->`). The LLM then reads the skeleton and fills in only the narrative portions, or the skeleton may be sufficient without LLM involvement for headless mode.
- **Estimated LLM tax:** ~500-1,000 tokens per invocation (reading verdict JSON, formatting tables, listing all findings with file paths, constructing remediation suggestions). The structured portion is ~300-600 tokens that a script would eliminate. In headless mode, the script could potentially eliminate the LLM from Step 6 entirely.
- **Note:** Medium severity because the report is the primary output artifact. In headless mode, a purely template-based report may be fully sufficient (no human reads it — it is an audit artifact). In interactive mode, the LLM narrative adds value for human consumption. A template script would also ensure consistent formatting across runs.

### Finding 3 — Findings File Aggregation and Output Routing (Steps 1-3 orchestration)

- **Severity:** Low
- **File:** `SKILL.md`, lines 38-51
- **Current work in prompt:** The LLM must execute each script, capture its JSON output, route the output to the correct findings file in `{output_folder}/reports/` (artifacts-findings.json, crossref-findings.json, placeholder-findings.json), and decide whether to proceed based on exit codes. While the scripts themselves handle the validation, the LLM is responsible for the plumbing: running the right command with the right flags, saving output to the right file, and interpreting the exit code for flow control.
- **Determinism test:** The orchestration sequence is fully deterministic: run script A with flags X, save to file Y, check exit code, if fail then stop. Steps 2-3 are explicitly marked as parallel. This is a pipeline pattern that a shell script or Python orchestrator can execute without LLM involvement.
- **Script alternative:** A `run-gate-pipeline.py` that: (a) runs `check-artifacts-exist.py` (fail-fast), (b) runs `validate-cross-references.py` and `check-placeholders.py` in parallel (subprocess), (c) saves all outputs to the correct report files, (d) returns a summary JSON with per-step status and whether to proceed to Step 4. The LLM then reads one summary instead of managing three script invocations.
- **Estimated LLM tax:** ~300-500 tokens per invocation (constructing three bash commands, parsing three JSON outputs, flow control logic, file routing). This is spread across Steps 1-3.
- **Note:** Low severity because the LLM is already efficient at running bash commands and the scripts are well-designed with proper exit codes. However, a pipeline script would reduce the number of LLM tool calls from 3+ to 1 and eliminate the risk of the LLM forgetting to save output to the correct file name. It would also make headless execution cleaner — a single script invocation for the entire deterministic portion.

### Finding 4 — Complementary Decisions Validation (Step 7)

- **Severity:** Low
- **File:** `SKILL.md`, lines 69-79
- **Current work in prompt:** "Confirm with the user: Tipo de tarefa, Manual necessario, Modelo de dados, Contagem APF. Record decisions in verdict.json." In headless mode: "Read from CLI args. Missing values use defaults."
- **Determinism test:** The headless path is entirely deterministic: read CLI args, apply defaults, write to verdict.json. The interactive path requires LLM for user conversation. In headless mode, the LLM is doing argument parsing and JSON writing — work that `calculate-gate-score.py` already handles via its `--task-type`, `--manual`, `--data-model`, `--apf-estimate` flags. The headless Step 7 is already subsumed by Step 5's script.
- **Script alternative:** No new script needed. In headless mode, Step 7's work is already done by `calculate-gate-score.py` which accepts all four complementary decision flags. The SKILL.md could be clarified to note that in headless mode, Step 7 is a no-op because Step 5 already records these values. This eliminates any LLM token spend on headless Step 7.
- **Estimated LLM tax:** ~100-200 tokens in headless mode (re-reading args, re-writing to verdict.json that already has the values). Zero in interactive mode (user conversation is inherently non-deterministic).
- **Note:** Low severity because this is more of a documentation/clarity issue than a missing script. The infrastructure already exists; the SKILL.md just does not make it explicit that headless Step 7 is handled by the score calculation script.

---

## 3. Aggregate Impact

| # | Finding | Severity | Tokens/invocation | Determinism % |
|---|---------|----------|-------------------|---------------|
| 1 | Test case structural pre-analysis | **Medium** | 200-400 | 100% (structural portion) |
| 2 | Report generation from template | **Medium** | 300-600 (up to 1,000 in headless) | ~70% (structured) / ~30% (narrative) |
| 3 | Findings aggregation pipeline | Low | 300-500 | 100% |
| 4 | Headless complementary decisions | Low | 100-200 (headless only) | 100% |

**Total estimated LLM tax on deterministic work:** 900-1,700 tokens per full pipeline run (interactive mode); up to 1,900-2,700 tokens in headless mode where the report template could replace the LLM entirely.

**Context:** This skill is already the best-optimized in the TJCE skill suite. The four existing scripts handle the heaviest deterministic operations with proper JSON contracts, exit codes, and test coverage. The remaining LLM usage (test case quality assessment and report generation) is well-targeted — both are tasks where semantic understanding adds genuine value. The findings here are incremental optimizations that sharpen the already-clean boundary between script and LLM work. The highest-value opportunity is the test case pre-analysis (Finding 1), which both reduces tokens and improves the LLM's focus on the semantic task it is uniquely qualified for.

**Priority ranking by ROI (savings vs. implementation effort):**

1. **Finding 1 — Test case structural pre-analysis** (Medium / moderate implementation). Highest quality impact because it improves the LLM's focus on semantic assessment while catching structural gaps deterministically. A ~100-line script that parses CT blocks and validates section presence. Also produces a filtered input for the LLM, reducing its read burden.

2. **Finding 2 — Report generation template** (Medium / moderate implementation). Highest token savings in headless mode where the script could replace the LLM entirely. A ~120-line script that reads verdict.json and findings files, producing markdown tables and agent-remediation mappings. In interactive mode, it produces a skeleton the LLM fills with narrative.

3. **Finding 3 — Pipeline orchestrator** (Low / moderate implementation). Reduces tool call count from 3+ to 1 and eliminates plumbing errors. A ~80-line script that runs the three existing scripts in sequence (with parallelism for Steps 2-3) and aggregates results. Most valuable for headless mode where it could chain with Finding 2 to make the entire deterministic path a single script invocation.

4. **Finding 4 — Headless Step 7 clarification** (Low / trivial implementation). No new code needed. Update SKILL.md to explicitly note that `calculate-gate-score.py` already handles complementary decisions in headless mode, making Step 7 a documented no-op for headless.

---

## 4. What Is Correctly Kept as Prompt

The following operations in the SKILL.md **should remain as LLM work**:

- **Test case semantic quality assessment** (Step 4 core) — Evaluating whether an expected result is "truly verifiable" requires understanding the business domain, the test scenario, and what constitutes an observable/measurable outcome. This is the skill's primary value-add and cannot be scripted.
- **Remediation narrative generation** (Step 6 interactive) — Explaining why a specific finding matters, which agent to invoke with what context, and how to prioritize fixes requires contextual reasoning about the project state.
- **Scope confirmation in interactive mode** (On Activation) — Identifying the feature being validated and confirming expected artifacts with the user is conversational work.
- **Interactive complementary decisions** (Step 7 interactive) — Asking the user about task type, manual requirement, data model applicability, and APF estimate requires natural conversation and may involve clarification.
- **Human gate management** (Step 8) — Presenting results, capturing APROVADO/AJUSTAR/REJEITAR decisions, and recording feedback with actionable next steps requires human interaction understanding.
- **Fail-fast communication** (Step 1 response) — When artifacts are missing, explaining which specific agents to invoke and why is more helpful than a raw JSON error. The script provides the data; the LLM provides the guidance.

---

## 5. Recommendations

### Immediate (Finding 1 — reduce ~200-400 tokens, improve quality focus)

Create one script:

1. **`scripts/pre-analyze-test-cases.py`** — Parses `{output_folder}/tests/test-cases.md` into individual CT blocks. For each CT block: checks presence of required sections (preconditions, steps, expected result/resultado esperado), validates that expected result is non-empty and has minimum substantive content (>10 words), verifies at least one cross-reference ID (RN or US) is present. Returns JSON with: per-CT structural findings, list of CTs that need LLM semantic review (passed structural checks), and list of CTs that failed structurally (no LLM review needed — deterministic failure). Input: output_folder. Output: JSON with `structural_findings` array and `llm_review_candidates` array.

### Short-term (Finding 2 — reduce ~300-600 tokens, enable fully-scripted headless reports)

2. **`scripts/generate-report-skeleton.py`** — Reads `gate-check-verdict.json` and all `*-findings.json` files. Produces a markdown report with:
   - Header: score badge, status, timestamp, threshold
   - Layer breakdown table (completeness/cross-reference/quality scores)
   - All findings as a structured table (severity | category | location | issue | fix)
   - Agent remediation mapping using a static category-to-agent table
   - In headless mode (`--headless` flag): produces the complete report, eliminating LLM from Step 6
   - In interactive mode: includes `<!-- NARRATIVE -->` markers where the LLM adds contextual guidance

### Architecture note

The skill's existing script suite is a model for other skills to follow. The consistent JSON contract across all four scripts (findings array, severity levels, summary counts) and the clear input chain (script outputs feed `calculate-gate-score.py`) demonstrate excellent pipeline design. The recommended additions (Findings 1-2) extend this pattern by adding pre-processing and post-processing scripts at the boundaries of the two remaining LLM tasks, further narrowing the LLM's role to pure semantic judgment. Finding 3 (pipeline orchestrator) is optional — it improves operational efficiency but does not change the determinism boundary.
