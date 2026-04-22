#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Validate that all expected release artifacts exist based on task type and flags."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ALWAYS_REQUIRED = [
    "CHANGELOG.md",
    "deploy-checklist.md",
    "rollback-plan.md",
    "PML.md",
]

STAGE_2_ARTIFACTS = [
    "CHANGELOG.md",
    "deploy-checklist.md",
    "rollback-plan.md",
]

APF_ARTIFACTS = [
    "apf/contagem-detalhada.md",
    "apf/resumo-apf.md",
]

MANUAL_ARTIFACTS = [
    "manual/manual-usuario.md",
]


def check_deliverables(output_folder: Path, task_type: str, manual_required: bool, stage: int | None = None) -> dict:
    findings = []
    release_dir = output_folder / "release"

    if stage == 2:
        return _check_stage_artifacts(release_dir, STAGE_2_ARTIFACTS, output_folder, task_type, manual_required)

    for artifact in ALWAYS_REQUIRED:
        path = release_dir / artifact
        if not path.exists():
            findings.append({
                "severity": "critical",
                "category": "deliverable",
                "location": {"file": str(path)},
                "issue": f"Artefato obrigatorio ausente: {artifact}",
                "fix": _fix_for(artifact),
            })
        elif path.stat().st_size == 0:
            findings.append({
                "severity": "critical",
                "category": "deliverable",
                "location": {"file": str(path)},
                "issue": f"Artefato vazio: {artifact}",
                "fix": f"Re-execute o step que produz {artifact}",
            })

    if task_type != "correcao_garantia":
        for artifact in APF_ARTIFACTS:
            path = release_dir / artifact
            if not path.exists():
                findings.append({
                    "severity": "critical",
                    "category": "deliverable",
                    "location": {"file": str(path)},
                    "issue": f"Artefato APF ausente: {artifact}",
                    "fix": "Execute tjce-agent-apf (Step 5)",
                })
    else:
        apf_resumo = release_dir / "apf" / "resumo-apf.md"
        if not apf_resumo.exists():
            findings.append({
                "severity": "medium",
                "category": "deliverable",
                "location": {"file": str(apf_resumo)},
                "issue": "Resumo APF placeholder ausente para correcao em garantia",
                "fix": "Step 5 deve gerar placeholder com PF = 0",
            })

    if manual_required:
        for artifact in MANUAL_ARTIFACTS:
            path = release_dir / artifact
            if not path.exists():
                findings.append({
                    "severity": "critical",
                    "category": "deliverable",
                    "location": {"file": str(path)},
                    "issue": f"Manual do usuario ausente: {artifact}",
                    "fix": "Execute tjce-agent-docs (Step 6)",
                })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    status = "fail" if critical > 0 else "pass"

    checklist = _generate_checklist(release_dir, task_type, manual_required)

    return {
        "script": "check-deliverables",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "task_type": task_type,
        "manual_required": manual_required,
        "checklist": checklist,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": 0,
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": 0,
        },
    }


def _check_stage_artifacts(release_dir: Path, artifacts: list[str], output_folder: Path, task_type: str, manual_required: bool) -> dict:
    findings = []
    for artifact in artifacts:
        path = release_dir / artifact
        if not path.exists():
            findings.append({
                "severity": "critical",
                "category": "deliverable",
                "location": {"file": str(path)},
                "issue": f"Artefato obrigatorio ausente: {artifact}",
                "fix": _fix_for(artifact),
            })
        elif path.stat().st_size == 0:
            findings.append({
                "severity": "critical",
                "category": "deliverable",
                "location": {"file": str(path)},
                "issue": f"Artefato vazio: {artifact}",
                "fix": f"Re-execute o step que produz {artifact}",
            })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    checklist = [{"artifact": a, "present": (release_dir / a).exists(), "size": (release_dir / a).stat().st_size if (release_dir / a).exists() else 0} for a in artifacts]

    return {
        "script": "check-deliverables",
        "version": "1.1.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else "pass",
        "task_type": task_type,
        "manual_required": manual_required,
        "stage_filter": 2,
        "checklist": checklist,
        "findings": findings,
        "summary": {"total": len(findings), "critical": critical, "high": 0, "medium": 0, "low": 0},
    }


def _fix_for(artifact: str) -> str:
    fixes = {
        "CHANGELOG.md": "Execute tjce-agent-release (Step 2)",
        "deploy-checklist.md": "Execute tjce-agent-release (Step 2)",
        "rollback-plan.md": "Execute tjce-agent-release (Step 2)",
        "PML.md": "Execute tjce-agent-release PML (Step 3)",
    }
    return fixes.get(artifact, f"Re-execute o step que produz {artifact}")


def _generate_checklist(release_dir: Path, task_type: str, manual_required: bool) -> list[dict]:
    items = []
    all_artifacts = list(ALWAYS_REQUIRED)
    if task_type != "correcao_garantia":
        all_artifacts.extend(APF_ARTIFACTS)
    else:
        all_artifacts.append("apf/resumo-apf.md")
    if manual_required:
        all_artifacts.extend(MANUAL_ARTIFACTS)

    for artifact in all_artifacts:
        path = release_dir / artifact
        items.append({
            "artifact": artifact,
            "present": path.exists(),
            "size": path.stat().st_size if path.exists() else 0,
        })
    return items


def format_markdown(result: dict) -> str:
    lines = ["# Ship Checklist — Entregaveis", ""]
    lines.append(f"**Tipo:** {result['task_type']}  ")
    lines.append(f"**Manual requerido:** {'Sim' if result['manual_required'] else 'Nao'}  ")
    lines.append(f"**Status:** {result['status'].upper()}")
    lines.append("")
    lines.append("| Artefato | Status |")
    lines.append("| -------- | ------ |")
    for item in result["checklist"]:
        mark = "Presente" if item["present"] else "**AUSENTE**"
        lines.append(f"| `{item['artifact']}` | {mark} |")
    lines.append("")
    if result["findings"]:
        lines.append("## Problemas")
        lines.append("")
        for f in result["findings"]:
            lines.append(f"- **[{f['severity'].upper()}]** {f['issue']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Validate that all expected release artifacts exist.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "--task-type",
        choices=("nova_funcionalidade", "mudanca", "correcao_garantia"),
        required=True,
        help="Task type for conditional artifact checking",
    )
    parser.add_argument(
        "--manual-required",
        action="store_true",
        help="Whether user manual is required",
    )
    parser.add_argument(
        "--stage",
        type=int,
        choices=(2,),
        help="Check only artifacts from a specific step (e.g., --stage 2)",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write JSON output to file instead of stdout",
    )
    parser.add_argument(
        "--format",
        choices=("json", "markdown"),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    if args.verbose:
        print(f"Checking deliverables in: {args.output_folder}", file=sys.stderr)

    result = check_deliverables(args.output_folder, args.task_type, args.manual_required, stage=args.stage)

    if args.format == "markdown":
        output = format_markdown(result)
    else:
        output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()
