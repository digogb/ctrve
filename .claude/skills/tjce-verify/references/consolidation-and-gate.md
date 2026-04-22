---
name: consolidation-and-gate
description: Steps 5-6 — Aggregate results from all verification layers into Go/No-Go recommendation and present to PO for human approval.
---

# Stages 5-6 — Consolidacao e Gate Humano

## Stage 5 — Consolidacao

Aggregate results from all three verification layers into a single decision report.

**Run the consolidation script to produce both JSON and markdown:**

```bash
python3 scripts/consolidate-results.py {output_folder} --threshold {coverage_threshold} -o {output_folder}/reports/verify-verdict.json
python3 scripts/consolidate-results.py {output_folder} --threshold {coverage_threshold} --format markdown -o {output_folder}/reports/verify-summary.md
```

The script reads all layer reports, aggregates metrics, and determines the verdict.

**Go/No-Go logic:**
- **GO:** Zero Alta defects, zero critical security findings, coverage >= threshold, coverage parseable
- **GO COM RESSALVAS:** Zero Alta, zero critical security, coverage >= threshold, but Media defects or high security findings exist
- **NO-GO:** Any Alta defect, any critical security finding, coverage below threshold, or coverage not parseable

**Output:** Both `verify-verdict.json` (for automation) and `verify-summary.md` (for humans) are produced by the script — no LLM formatting needed.

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

Generate `verify-summary.md` with status **"AGUARDANDO HOMOLOGACAO"**. The report contains all data needed for a human to decide asynchronously. Write `verify-state.json` with stage=6 and status=awaiting_approval. Exit with code 2.

**Stage complete.** Verification pipeline finished.
