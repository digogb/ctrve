#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Layer 1: Check that all required SPEC artifacts exist and are non-empty."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_ARTIFACTS = [
    "requirements/user-stories.md",
    "requirements/business-rules.md",
    "requirements/messages.md",
    "requirements/product-vision.md",
    "tests/test-cases.md",
]

REQUIRED_ARCHITECTURE = "architecture/"

CONDITIONAL_ARTIFACTS = {
    "data_model": "architecture/data-model.md",
    "ux": "ux/",
}

RECOMMENDED_ARTIFACTS = [
    "architecture/threat-model.md",
]


def check_artifacts(output_folder: Path, data_model: bool, ux: bool) -> dict:
    findings = []

    arch_dir = output_folder / "architecture"
    if not arch_dir.exists() or not any(arch_dir.iterdir()):
        findings.append({
            "severity": "critical",
            "category": "completeness",
            "location": {"file": str(arch_dir)},
            "issue": "Diretorio architecture/ ausente ou vazio",
            "fix": "Execute o agente de arquitetura para gerar tech-design",
        })
    else:
        has_tech = any(
            f.name.startswith("tech") and f.suffix == ".md"
            for f in arch_dir.iterdir() if f.is_file()
        )
        if not has_tech:
            findings.append({
                "severity": "critical",
                "category": "completeness",
                "location": {"file": str(arch_dir)},
                "issue": "architecture/ nao contem tech-design",
                "fix": "Execute o agente de arquitetura para gerar tech-design",
            })

    for artifact in REQUIRED_ARTIFACTS:
        path = output_folder / artifact
        if not path.exists():
            findings.append({
                "severity": "critical",
                "category": "completeness",
                "location": {"file": str(path)},
                "issue": f"Artefato obrigatorio ausente: {artifact}",
                "fix": _fix_for(artifact),
            })
        elif not path.read_text(encoding="utf-8", errors="ignore").strip():
            findings.append({
                "severity": "critical",
                "category": "completeness",
                "location": {"file": str(path)},
                "issue": f"Artefato vazio: {artifact}",
                "fix": f"Re-execute o agente que produz {artifact}",
            })

    if data_model:
        dm_path = output_folder / CONDITIONAL_ARTIFACTS["data_model"]
        if not dm_path.exists():
            findings.append({
                "severity": "critical",
                "category": "completeness",
                "location": {"file": str(dm_path)},
                "issue": "data-model.md ausente (flag --data-model ativo)",
                "fix": "Execute o agente de arquitetura para gerar data-model",
            })

    if ux:
        ux_dir = output_folder / "ux"
        if not ux_dir.exists() or not any(ux_dir.iterdir()):
            findings.append({
                "severity": "critical",
                "category": "completeness",
                "location": {"file": str(output_folder / "ux")},
                "issue": "Diretorio ux/ ausente ou vazio (flag --ux ativo)",
                "fix": "Gere os artefatos de UX antes de prosseguir",
            })

    for artifact in RECOMMENDED_ARTIFACTS:
        path = output_folder / artifact
        if not path.exists():
            findings.append({
                "severity": "low",
                "category": "completeness",
                "location": {"file": str(path)},
                "issue": f"Artefato recomendado ausente: {artifact}",
                "fix": f"Considere gerar {artifact} para maior cobertura",
            })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {
        "script": "check-artifacts-exist",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else "pass",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": 0,
            "medium": 0,
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


def _fix_for(artifact: str) -> str:
    fixes = {
        "requirements/user-stories.md": "Execute tjce-agent-requirements para gerar user stories",
        "requirements/business-rules.md": "Execute tjce-agent-requirements para gerar regras de negocio",
        "requirements/messages.md": "Execute tjce-agent-requirements para gerar mensagens",
        "requirements/product-vision.md": "Execute tjce-agent-requirements para gerar visao do produto",
        "tests/test-cases.md": "Execute tjce-agent-qa capability BUILD para gerar casos de teste",
    }
    return fixes.get(artifact, f"Gere o artefato {artifact}")


def main():
    parser = argparse.ArgumentParser(
        description="Check that all required SPEC artifacts exist.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
    )
    parser.add_argument(
        "--data-model",
        action="store_true",
        help="Require data-model.md (project involves database)",
    )
    parser.add_argument(
        "--ux",
        action="store_true",
        help="Require UX artifacts (project has user interface)",
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
        print(f"Checking artifacts in: {args.output_folder}", file=sys.stderr)

    result = check_artifacts(args.output_folder, args.data_model, args.ux)

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
