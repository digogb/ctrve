# Structure & Capabilities Analysis: tjce-agent-release

**Scanner:** StructureBot
**Date:** 2026-04-16
**Agent:** tjce-agent-release
**Memory Agent:** No

---

## Assessment

The agent is structurally solid with a well-designed SKILL.md covering all required sections, a focused set of three capabilities with clear routing, and comprehensive headless mode support. The primary structural issues are: (1) the pre-pass flagged a missing `## On Activation` section because the actual heading uses a non-standard suffix ("On Activation -- Intent Before Ingestion"), and (2) all three capability prompts lack progression condition keywords, meaning there is no defined criteria for when a capability is "done" and control should return. The agent's identity, principles, and communication style are domain-specific and effective, not generic filler.

---

## Sections Found

| Section | Status | Notes |
|---------|--------|-------|
| Overview | Present (line 8) | Complete, domain-specific |
| Identity | Present (line 21) | Actionable one-sentence persona |
| Communication Style | Present (line 25) | 5 concrete examples |
| Principles | Present (line 33) | 4 guiding principles, domain-specific |
| On Activation | Present (line 40) | Heading is `## On Activation -- Intent Before Ingestion` -- pre-pass flagged as missing due to non-standard suffix |
| Prerequisite Check | Present (line 56) | Subsection of On Activation |
| Data Collection Pre-Pass | Present (line 64) | Parallel script execution |
| Capability Routing | Present (line 78) | 3 capabilities, table format |
| Post-Generation Validation | Present (line 88) | Script-based validation |
| Headless Contract | Present (line 95) | Complete with exit codes, args resolution, JSON output |

**Missing standard sections:** None (all required sections present).
**Invalid sections:** None.

---

## Capabilities Inventory

| Capability | Code | Route | File Exists | Structural Issues |
|-----------|------|-------|-------------|-------------------|
| PML -- Plano de Mudanca e Liberacao | P | `./references/pml.md` | Yes | No progression conditions |
| CHANGELOG -- Release Notes por estoria | C | `./references/changelog.md` | Yes | No progression conditions |
| DEPLOY -- Checklist de implantacao e rollback | D | `./references/deploy.md` | Yes | No progression conditions |

### Per-Capability Notes

**pml.md** -- Well-structured with 7 generation steps, clear output template, fallback paths for when pre-pass data is unavailable, and headless mode behavior. Config header present. Declares success criteria ("What Success Looks Like") with 6 specific checks. No progression condition defining when the capability is complete and should hand back control.

**changelog.md** -- Clean 4-step generation flow, clear output template, fallback to raw Git log. Config header present. Success criteria defined with 4 checks. No progression condition.

**deploy.md** -- Produces two output files (deploy-checklist.md and rollback-plan.md), 4-step generation, conditional section inclusion based on detected changes. Config header present. Success criteria defined with 5 checks. No progression condition.

---

## Key Findings

### HIGH: Pre-pass reports missing `## On Activation` section (false positive)

- **File:** `SKILL.md:40`
- **Issue:** The pre-pass flagged `Missing ## On Activation section` because the heading is `## On Activation -- Intent Before Ingestion` instead of the canonical `## On Activation`. The section exists and is complete.
- **Fix:** Rename heading to `## On Activation` to match the expected standard format. The subtitle can be moved to a paragraph below the heading if desired.

### HIGH: No progression conditions in any capability prompt

- **Files:** `references/pml.md:96`, `references/changelog.md:96`, `references/deploy.md:150`
- **Issue:** All three capability prompts lack progression condition keywords (e.g., "proceed when", "complete when", "done when"). Without these, the agent has no defined signal for when a capability execution is finished and should return control to the routing layer.
- **Fix:** Add a `## Done When` or `## Completion Criteria` section to each capability prompt. For example, pml.md could end with: "Complete when `{output_folder}/release/PML.md` is written and all 6 sections are populated (no PENDENTE markers in interactive mode)."

### MEDIUM: PML capability partially overlaps with Deploy capability

- **Files:** `references/pml.md`, `references/deploy.md`
- **Issue:** PML sections 4 (Procedimento de Implantacao), 5 (Procedimento de Rollback), and 6 (Validacao Pos-Implantacao) substantially overlap with the Deploy capability's checklist and rollback plan. When `--task-type all` runs, similar content is generated twice with potential for inconsistency between the PML and the deploy/rollback artifacts.
- **Fix:** Consider having PML sections 4-6 reference the deploy artifacts instead of generating duplicate content, or add explicit guidance that PML should summarize while deploy artifacts provide full detail. At minimum, add a note in pml.md that when running alongside deploy capability, sections 4-6 should be consistent with the generated deploy-checklist.md and rollback-plan.md.

### LOW: Capability prompts include step-by-step generation procedures

- **Files:** `references/pml.md`, `references/changelog.md`, `references/deploy.md`
- **Issue:** Each capability prompt has detailed "Passos de Geracao" sections (7 steps in PML, 4 in CHANGELOG, 4 in Deploy) that procedurally describe what the LLM should do. Given the agent's strong identity as a meticulous release manager and the clear output templates, much of this procedural guidance is what the LLM would do naturally from the template and success criteria.
- **Fix:** This is a minor concern since the procedures contain domain-specific knowledge (TJCE deploy order, Alembic-specific commands, US-NNN mapping logic) that is genuinely useful. No action required unless token budget becomes a concern. If trimming is needed, the procedures could be reduced to decision points and non-obvious rules only.

---

## Strengths

1. **Strong domain-specific identity and principles.** The identity ("Gerente de release que trata cada artefato de implantacao como documento oficial do tribunal") directly primes the behavior. Principles like "PML e artefato oficial" and "Rollback SEMPRE" create clear decision frameworks. None are generic platitudes.

2. **Communication style is concrete and actionable.** Five specific style rules with examples of good vs. bad output ("Execute migration X antes de deploy Y" vs. "ajuste conforme necessario"). Style matches the formal release management domain.

3. **Description quality is excellent.** Follows the two-part format with specific trigger phrases ("generate release artifacts", "create PML", "prepare deployment", "generate changelog", "plan rollback"). Conservative activation requiring explicit user request.

4. **Complete headless mode support.** SKILL.md defines exit codes, args resolution order, default derivation logic, and structured JSON output. Each capability prompt has its own headless section with specific behavior.

5. **Robust data pipeline.** Parallel pre-pass scripts (`extract-git-changelog.py`, `detect-deploy-changes.py`) with fallback paths when scripts are unavailable. Post-generation validation script. All three scripts have corresponding test files.

6. **Capability prompts have config headers and success criteria.** Every prompt starts with a config note about variable resolution and defines "What Success Looks Like" with numbered specific checks.

7. **Logical activation sequence.** Intent determination first, then prerequisites, then data collection, then routing. The ordering is correct -- you determine what to generate before checking prerequisites for it.

---

## Memory & Headless Status

**Memory:** Not applicable. This is a stateless agent (`is_memory_agent: false`). No memory paths detected. No memory-related files needed.

**Headless:** Fully configured. The SKILL.md `### Headless Contract` section defines:
- Exit codes (0, 1, 2) with clear semantics
- Args resolution order (CLI > config > prompt > default)
- Default derivation for missing flags (`--since`, `--project`, `--version`, `--responsible`)
- Structured JSON output schema with `--json` flag
- Each capability prompt also has its own headless behavior section

No issues detected with headless setup.

---

## Pre-Pass Findings (Preserved)

| File | Line | Severity | Category | Issue |
|------|------|----------|----------|-------|
| SKILL.md | 1 | high | sections | Missing ## On Activation section |
| changelog.md | 96 | high | progression | No progression condition keywords found |
| deploy.md | 150 | high | progression | No progression condition keywords found |
| pml.md | 160 | high | progression | No progression condition keywords found |

**Note on SKILL.md finding:** This is a false positive. The section exists at line 40 as `## On Activation -- Intent Before Ingestion`. The pre-pass pattern matching did not recognize the non-standard suffix. Recommend renaming to `## On Activation` for compliance.
