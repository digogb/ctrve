---
name: consolidation-and-gate
description: Steps 5-6 — Aggregate results from all verification layers into Go/No-Go recommendation and present to PO for human approval.
---

**Config note:** Variables `{project-root}`, `{output_folder}`, `{communication_language}`, `{document_output_language}`, and `{coverage_threshold}` are resolved by SKILL.md at activation time.

# Stages 5-6 — Consolidacao e Gate Humano

## Stage 5 — Consolidacao

Aggregate results from all three verification layers into a single decision report.

**Run the consolidation script:**

```bash
python3 scripts/consolidate-results.py {output_folder} --threshold {coverage_threshold}
```

The script reads:
- `{output_folder}/reports/verify-layer1-automated.md`
- `{output_folder}/reports/test-cycle-N.md` (latest cycle)
- `{output_folder}/reports/security-report.md`

**Output:** `{output_folder}/reports/verify-summary.md` containing:
- Executive summary with Go/No-Go verdict
- Per-layer results overview
- Consolidated findings by severity
- Coverage metrics and threshold status
- Risk assessment
- Specific conditions (if GO COM RESSALVAS)

**Go/No-Go logic:**
- **GO:** Zero Alta defects, zero critical security findings, coverage >= threshold
- **GO COM RESSALVAS:** Zero Alta, zero critical security, coverage >= threshold, but Media defects or high security findings exist — each listed with status
- **NO-GO:** Any Alta defect, any critical security finding, or coverage below threshold

Use the script's JSON output to generate the markdown summary. The script provides the verdict and all metrics — the workflow formats the human-readable report.

## Stage 6 — Gate Humano (Parada Obrigatoria)

Human approval is **never automated**. This is the final quality gate before release.

### Interactive Mode

Present the verify-summary content to the PO clearly and actionably:

- Headline: **GO** / **GO COM RESSALVAS** / **NO-GO**
- Key metrics: coverage %, defect counts by severity, security findings
- If GO COM RESSALVAS: list each caveat requiring acknowledgment

**Await PO decision:**

| Decisao | Acao |
| ------- | ---- |
| **APROVADO** | Mark verify-summary.md as approved with PO name and timestamp. Feature cleared for deployment. |
| **AJUSTAR** | Capture specific feedback from PO. Update verify-summary.md with adjustment requests. Return to BUILD with the specific items to address. |
| **REJEITAR** | Capture rejection reason. Update verify-summary.md with rejection. Return to SPEC phase for requirements revision. |

### Headless Mode

Generate `verify-summary.md` with status **"AGUARDANDO HOMOLOGACAO"**. The report contains all data needed for a human to decide asynchronously. Exit with code 2.
