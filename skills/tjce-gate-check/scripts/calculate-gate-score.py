#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Calculate weighted gate score from all layer findings and produce verdict."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PASS_THRESHOLD = 90

LAYER_WEIGHTS = {
    "completeness": 40,
    "cross-reference": 30,
    "quality": 30,
}

SEVERITY_DEDUCTIONS = {
    "critical": 1.0,
    "high": 0.5,
    "medium": 0.2,
    "low": 0.0,
}

CATEGORY_TO_LAYER = {
    "completeness": "completeness",
    "cross-reference": "cross-reference",
    "orphan-id": "cross-reference",
    "placeholder": "quality",
    "empty-section": "quality",
    "format": "quality",
    "coverage": "quality",
    "test-quality": "quality",
}


def calculate_score(output_folder: Path, task_type: str | None, manual: bool,
                    data_model: bool, apf_estimate: float | None) -> dict:
    reports_dir = output_folder / "reports"
    findings_files = [
        reports_dir / "artifacts-findings.json",
        reports_dir / "crossref-findings.json",
        reports_dir / "placeholder-findings.json",
        reports_dir / "quality-findings.json",
    ]

    all_findings = []
    missing_inputs = []
    for ff in findings_files:
        if ff.exists():
            try:
                data = json.loads(ff.read_text(encoding="utf-8"))
                all_findings.extend(data.get("findings", []))
            except (json.JSONDecodeError, OSError):
                missing_inputs.append(str(ff))
        else:
            missing_inputs.append(str(ff))

    layer_scores = {}
    for layer, max_points in LAYER_WEIGHTS.items():
        layer_findings = [
            f for f in all_findings
            if CATEGORY_TO_LAYER.get(f.get("category", ""), "quality") == layer
        ]

        deductions = sum(
            SEVERITY_DEDUCTIONS.get(f.get("severity", "low"), 0)
            for f in layer_findings
        )

        max_deductions = max_points / 10
        normalized_deduction = min(deductions / max_deductions, 1.0) * max_points if max_deductions > 0 else 0
        layer_scores[layer] = max(0, round(max_points - normalized_deduction, 1))

    total_score = round(sum(layer_scores.values()), 1)

    has_critical = any(f.get("severity") == "critical" for f in all_findings)
    has_placeholder = any(f.get("category") == "placeholder" for f in all_findings)
    has_missing_artifact = any(
        f.get("severity") == "critical" and f.get("category") == "completeness"
        for f in all_findings
    )

    if has_missing_artifact:
        status = "FAIL"
        fail_reason = "Artefatos obrigatorios ausentes"
    elif has_placeholder:
        status = "FAIL"
        fail_reason = "Placeholders encontrados em artefatos"
    elif total_score < PASS_THRESHOLD:
        status = "FAIL"
        fail_reason = f"Score {total_score} abaixo do minimo {PASS_THRESHOLD}"
    else:
        status = "PASS"
        fail_reason = None

    warnings = [
        f for f in all_findings
        if f.get("severity") in ("medium", "low")
    ]
    missing = [
        f for f in all_findings
        if f.get("severity") == "critical"
    ]

    verdict = {
        "script": "calculate-gate-score",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "score": total_score,
        "threshold": PASS_THRESHOLD,
        "status": status,
        "fail_reason": fail_reason,
        "layer_scores": layer_scores,
        "missing": [{"issue": f["issue"], "fix": f.get("fix", "")} for f in missing],
        "warnings": [{"issue": f["issue"], "severity": f["severity"]} for f in warnings],
        "task_type": task_type,
        "manual_required": manual,
        "data_model_required": data_model,
        "apf_estimate": apf_estimate,
        "missing_inputs": missing_inputs,
        "findings_count": len(all_findings),
        "summary": {
            "total": len(all_findings),
            "critical": sum(1 for f in all_findings if f.get("severity") == "critical"),
            "high": sum(1 for f in all_findings if f.get("severity") == "high"),
            "medium": sum(1 for f in all_findings if f.get("severity") == "medium"),
            "low": sum(1 for f in all_findings if f.get("severity") == "low"),
        },
    }
    return verdict


def main():
    parser = argparse.ArgumentParser(
        description="Calculate weighted gate score and produce verdict.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "--task-type",
        choices=("nova_funcionalidade", "mudanca", "correcao_garantia"),
        help="Task type",
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Manual is required",
    )
    parser.add_argument(
        "--data-model",
        action="store_true",
        help="Data model applies",
    )
    parser.add_argument(
        "--apf-estimate",
        type=float,
        help="Estimated APF count",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write JSON output to file instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Calculating gate score for: {args.output_folder}", file=sys.stderr)

    result = calculate_score(
        args.output_folder, args.task_type, args.manual,
        args.data_model, args.apf_estimate,
    )

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
