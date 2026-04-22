#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Check that tjce-verify completed with APROVADO status."""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def check_verify_status(output_folder: Path) -> dict:
    findings = []

    verdict_path = output_folder / "reports" / "verify-verdict.json"
    summary_path = output_folder / "reports" / "verify-summary.md"

    status = None
    source = None

    if verdict_path.exists():
        try:
            data = json.loads(verdict_path.read_text(encoding="utf-8"))
            verdict = data.get("verdict", "")
            if verdict:
                status = verdict.upper()
                source = str(verdict_path)
        except (json.JSONDecodeError, OSError):
            pass

    if status is None and summary_path.exists():
        try:
            content = summary_path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"(?i)\baprovado\b", content):
                status = "APROVADO"
                source = str(summary_path)
            elif re.search(r"(?i)\baguardando\s+homologa", content):
                status = "AGUARDANDO HOMOLOGACAO"
                source = str(summary_path)
            elif re.search(r"(?i)\bno-go\b|rejeit", content):
                status = "REJEITADO"
                source = str(summary_path)
            else:
                status = "DESCONHECIDO"
                source = str(summary_path)
        except OSError:
            pass

    if status is None:
        findings.append({
            "severity": "critical",
            "category": "prerequisite",
            "location": {"file": str(output_folder / "reports")},
            "issue": "Nenhum relatorio de verificacao encontrado (verify-verdict.json ou verify-summary.md)",
            "fix": "Execute /tjce-verify primeiro",
        })
        return _build_result(output_folder, "fail", findings, status=None, source=None)

    if status != "APROVADO" and status != "GO":
        findings.append({
            "severity": "critical",
            "category": "prerequisite",
            "location": {"file": source},
            "issue": f"Verificacao nao aprovada — status atual: {status}",
            "fix": "Execute /tjce-verify e obtenha aprovacao do PO antes de prosseguir com ship",
        })
        return _build_result(output_folder, "fail", findings, status=status, source=source)

    staleness = _check_staleness(output_folder, verdict_path if verdict_path.exists() else summary_path)
    if staleness:
        findings.append(staleness)

    return _build_result(output_folder, "pass", findings, status=status, source=source)


def _check_staleness(output_folder: Path, verify_file: Path) -> dict | None:
    if not verify_file.exists():
        return None
    try:
        verify_mtime = verify_file.stat().st_mtime
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            capture_output=True, text=True, cwd=str(output_folder.parent),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return None
        latest_commit_time = float(result.stdout.strip())
        if latest_commit_time > verify_mtime:
            return {
                "severity": "high",
                "category": "staleness",
                "location": {"file": str(verify_file)},
                "issue": "Commits mais recentes que o relatorio de verificacao — resultado pode estar desatualizado",
                "fix": "Re-execute /tjce-verify para validar o estado atual do codigo",
            }
    except (OSError, ValueError):
        pass
    return None


def _build_result(output_folder, result_status, findings, status, source):
    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {
        "script": "check-verify-status",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": result_status,
        "verify_status": status,
        "verify_source": source,
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check that tjce-verify completed with APROVADO status.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
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
        print(f"Checking verify status in: {args.output_folder}", file=sys.stderr)

    result = check_verify_status(args.output_folder)

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
