# Script Opportunities Analysis — tjce-agent-release

**Scanner:** ScriptHunter
**Agent:** `skills/tjce-agent-release/`
**Date:** 2026-04-16

---

## Existing Scripts Inventory

The agent already has a mature script layer with three Python scripts and corresponding test suites:

| Script | Purpose | Lines | Tests |
|--------|---------|-------|-------|
| `scripts/extract-git-changelog.py` | Parses git log, groups commits by US-NNN, enriches with story titles from spec | 228 | `tests/test_extract-git-changelog.py` |
| `scripts/detect-deploy-changes.py` | Analyzes git diff for migrations, dependency changes, config changes | 293 | `tests/test_detect-deploy-changes.py` |
| `scripts/validate-release-artifacts.py` | Post-generation validation: empty sections, placeholders, rollback presence, US cross-reference | 260 | `tests/test_validate-release-artifacts.py` |

All three scripts follow PEP 723 inline metadata, use `argparse` with `--help`, output JSON, and define clear exit codes. This is a well-structured script layer.

---

## Assessment

This agent demonstrates strong script-first design. The heaviest deterministic operations -- Git log parsing, deploy change detection, and artifact validation -- are already delegated to Python scripts invoked as pre-pass and post-pass steps in `SKILL.md`. The remaining prompt work is primarily semantic: composing human-readable PML prose, writing context-appropriate rollback procedures, and drafting post-deployment validation checks tailored to specific user stories. The residual script opportunities are real but modest in token savings compared to agents that embed these operations in prompts.

---

## Key Findings

### Finding 1 — CHANGELOG Statistics Computation in Prompt

- **Severity:** Medium
- **LLM Tax:** ~150-250 tokens per invocation
- **Affected file:** `references/changelog.md:53-57`
- **What the LLM does now:** The CHANGELOG template includes a "Estatisticas" section requiring the LLM to compute `mapped/total`, percentage, stories count, and authors list. While `git-changelog.json` provides raw `stats` with `total`, `mapped`, `unmapped`, and `stories_count`, the LLM must still calculate the percentage, format the authors list, and compose the statistics block.
- **What a script would do:** Extend `extract-git-changelog.py` to emit a pre-formatted `stats_summary` field in the JSON output containing `mapped_pct` (already computed at line 213 but only for the console summary, not in the main JSON payload), `authors_formatted` (comma-separated), and a ready-to-paste statistics block.
- **Estimated savings:** ~150 tokens (computation + formatting)
- **Pre-pass potential:** Yes -- extend existing script's JSON output; zero new scripts needed
- **Integration:** The `mapped_pct` is already computed on line 213-214 of `extract-git-changelog.py` for the console message but is NOT included in the main `changelog` JSON written to file. Adding it to the main payload is a one-line fix.

### Finding 2 — Metadata Derivation in Headless Mode

- **Severity:** Low
- **LLM Tax:** ~80-120 tokens per invocation
- **Affected file:** `SKILL.md:102-103`
- **What the LLM does now:** In headless mode, the SKILL.md instructs the LLM to "derive `--project` from directory name, `--version` from Git tag, `--responsible` from `user_name` config." These are purely deterministic: directory basename, `git describe --tags`, and YAML key lookup.
- **What a script would do:** A small `resolve-release-metadata.py` script that reads `config.yaml`, inspects the Git repo, and emits a JSON object with `project`, `version`, `responsible`, `date`, and `des` (from flags or defaults). The LLM would receive resolved metadata instead of deriving it.
- **Estimated savings:** ~100 tokens (directory inspection + config parsing + tag detection)
- **Pre-pass potential:** Yes -- could run alongside the existing two pre-pass scripts
- **Standalone value:** Moderate -- any TJCE agent needing project metadata could reuse it
- **Reuse across skills:** High -- project name, version, and user name are common across TJCE agents

### Finding 3 — Prerequisite File Existence Checks

- **Severity:** Low
- **LLM Tax:** ~60-100 tokens per invocation
- **Affected file:** `SKILL.md:58-63`
- **What the LLM does now:** The On Activation section instructs the LLM to verify that `user-stories.md` exists, `tech-design.md` exists, and a Git repository with commits is present. These are pure filesystem existence checks.
- **What a script would do:** A `check-prerequisites.py` script (or a `--check-prereqs` flag on one of the existing scripts) that verifies file existence, Git repo status, and tag availability. Emits a JSON report: `{"git_ok": true, "stories_found": true, "tech_design_found": false, "last_tag": "v1.0.0", "warnings": ["tech-design.md not found"]}`.
- **Estimated savings:** ~80 tokens
- **Pre-pass potential:** Yes -- could be the first script in the pre-pass chain, gating subsequent scripts
- **Standalone value:** High -- usable as a CI lint check before release pipeline
- **Reuse across skills:** High -- prerequisite checking pattern is universal

### Finding 4 — PML Identification Table Generation

- **Severity:** Low
- **LLM Tax:** ~60-80 tokens per invocation
- **Affected file:** `references/pml.md:46-57`
- **What the LLM does now:** Generates a markdown table with 5 fixed fields (Sistema, Versao, Data prevista, Responsavel, Tarefa DES) from resolved metadata. This is a pure template fill operation.
- **What a script would do:** If metadata were resolved by a script (Finding 2), the identification table could be emitted as a pre-filled markdown fragment. The LLM would insert it verbatim.
- **Estimated savings:** ~70 tokens
- **Pre-pass potential:** Yes -- natural extension of metadata resolution script
- **Integration note:** Low priority because the table is small and the LLM handles it reliably. Only worth pursuing if Finding 2 is implemented.

### Finding 5 — Deploy Checklist Section Omission Logic

- **Severity:** Low
- **LLM Tax:** ~50-80 tokens per invocation
- **Affected file:** `references/deploy.md:126-131`
- **What the LLM does now:** Reads `deploy-changes.json` boolean flags (`has_migrations`, `has_backend_deps`, `has_frontend_deps`, `has_config_changes`) and decides which sections to include or omit. This is a deterministic branching decision based on boolean values.
- **What a script would do:** Extend `detect-deploy-changes.py` to emit an `applicable_sections` list (e.g., `["pre-deploy", "database", "backend", "frontend", "post-deploy"]`) based on the boolean flags. The LLM would skip the conditional logic and write only the listed sections.
- **Estimated savings:** ~60 tokens
- **Pre-pass potential:** Yes -- extend existing script output
- **Integration note:** Marginal benefit. The LLM already has the JSON booleans and the conditional logic is simple.

### Finding 6 — Fallback Git Command Execution

- **Severity:** Low
- **LLM Tax:** ~40-60 tokens per invocation (only on fallback path)
- **Affected files:** `references/changelog.md:64-70`, `references/deploy.md:113-119`
- **What the LLM does now:** Both CHANGELOG and Deploy capabilities include fallback instructions telling the LLM to manually execute the pre-pass scripts if the JSON files are unavailable. The LLM reads the instructions, formulates the command, and runs it.
- **What a script would do:** This is already handled correctly -- the prompts tell the LLM to invoke the existing scripts. However, the On Activation section in SKILL.md already runs these scripts as a pre-pass (lines 66-76). The fallback path should rarely trigger. No action needed beyond ensuring the pre-pass always runs.
- **Estimated savings:** ~0 tokens in normal flow; ~50 in fallback (rare)
- **Pre-pass potential:** N/A -- already a pre-pass

---

## Aggregate Savings

| Finding | Severity | Est. Tokens Saved | Frequency |
|---------|----------|-------------------|-----------|
| #1 Statistics computation | Medium | ~150-250 | Every changelog generation |
| #2 Metadata derivation | Low | ~80-120 | Every headless invocation |
| #3 Prerequisite checks | Low | ~60-100 | Every activation |
| #4 PML identification table | Low | ~60-80 | Every PML generation |
| #5 Section omission logic | Low | ~50-80 | Every deploy generation |
| #6 Fallback commands | Low | ~0-50 | Rare fallback only |

**Total estimated savings per full `--task-type all` invocation:** ~400-680 tokens

**Verdict:** The agent already exemplifies script-first design. The three existing scripts handle the heaviest deterministic work (Git parsing, change detection, artifact validation). Remaining opportunities are incremental refinements, not architectural gaps. The highest-value action is Finding 1 (adding `mapped_pct` and `authors_formatted` to the main JSON payload of `extract-git-changelog.py`) because it is a one-line fix to an existing script. Finding 2 (metadata resolution script) has the best reuse potential across TJCE agents. Findings 3-6 are nice-to-have optimizations with diminishing returns.
