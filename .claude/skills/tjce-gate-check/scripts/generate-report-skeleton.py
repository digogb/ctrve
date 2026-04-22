#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Generate gate-check report skeleton from verdict and findings JSON."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LAYER_NAMES = {
    "completeness": "Completude de Artefatos",
    "cross-reference": "Consistencia Cruzada",
    "quality": "Qualidade",
}


def generate_report(output_folder: Path) -> str:
    reports_dir = output_folder / "reports"
    verdict_path = reports_dir / "gate-check-verdict.json"

    if not verdict_path.exists():
        return "# Gate Check Report\n\n**Erro:** gate-check-verdict.json nao encontrado.\n"

    verdict = json.loads(verdict_path.read_text(encoding="utf-8"))

    lines = [
        "# Relatorio de Gate Check",
        "",
        f"**Data:** {verdict.get('timestamp', datetime.now(timezone.utc).isoformat())}",
        f"**Score:** {verdict['score']} / 100 (minimo: {verdict['threshold']})",
        f"**Status:** {verdict['status']}",
    ]

    if verdict.get("fail_reason"):
        lines.append(f"**Motivo:** {verdict['fail_reason']}")

    lines.extend(["", "## Score por Camada", ""])
    lines.append("| Camada | Score | Max |")
    lines.append("| ------ | ----- | --- |")
    for layer, score in verdict.get("layer_scores", {}).items():
        name = LAYER_NAMES.get(layer, layer)
        max_pts = {"completeness": 40, "cross-reference": 30, "quality": 30}.get(layer, "?")
        lines.append(f"| {name} | {score} | {max_pts} |")

    findings_files = {
        "Completude": "artifacts-findings.json",
        "Consistencia Cruzada": "crossref-findings.json",
        "Placeholders": "placeholder-findings.json",
        "Qualidade": "quality-findings.json",
    }

    for section_name, fname in findings_files.items():
        fpath = reports_dir / fname
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        findings = data.get("findings", [])
        if not findings:
            continue

        lines.extend(["", f"## {section_name}", ""])
        lines.append("| Severidade | Issue | Fix |")
        lines.append("| ---------- | ----- | --- |")
        for f in findings:
            sev = f.get("severity", "?")
            issue = f.get("issue", "").replace("|", "\\|")
            fix = f.get("fix", "").replace("|", "\\|")
            lines.append(f"| {sev} | {issue} | {fix} |")

    if verdict.get("missing_inputs"):
        lines.extend(["", "## Entradas Ausentes", ""])
        for mi in verdict["missing_inputs"]:
            lines.append(f"- {mi}")

    if verdict.get("warnings"):
        lines.extend(["", "## Avisos", ""])
        for w in verdict["warnings"]:
            lines.append(f"- [{w.get('severity', '?')}] {w.get('issue', '')}")

    if verdict.get("task_type"):
        lines.extend([
            "",
            "## Decisoes Complementares",
            "",
            f"- **Tipo de tarefa:** {verdict['task_type']}",
            f"- **Manual necessario:** {'Sim' if verdict.get('manual_required') else 'Nao'}",
            f"- **Modelo de dados:** {'Sim' if verdict.get('data_model_required') else 'Nao'}",
        ])
        if verdict.get("apf_estimate") is not None:
            lines.append(f"- **Estimativa APF:** {verdict['apf_estimate']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate gate-check report from verdict and findings.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write report to file instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Generating report for: {args.output_folder}", file=sys.stderr)

    report = generate_report(args.output_folder)

    if args.output:
        args.output.write_text(report, encoding="utf-8")
        if args.verbose:
            print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
