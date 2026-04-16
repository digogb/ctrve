#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Aggregate verification layer results into a Go/No-Go recommendation report."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def find_latest_test_cycle(reports_dir: Path) -> Path | None:
    cycles = sorted(reports_dir.glob("test-cycle-*.md"))
    return cycles[-1] if cycles else None


def extract_coverage(layer1_path: Path) -> float | None:
    if not layer1_path.exists():
        return None
    content = layer1_path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        r"(?i)cobertura[:\s]*(\d+(?:\.\d+)?)\s*%|coverage[:\s]*(\d+(?:\.\d+)?)\s*%",
        content,
    )
    if match:
        return float(match.group(1) or match.group(2))
    return None


def count_defects_by_severity(cycle_path: Path) -> dict:
    counts = {"alta": 0, "media": 0, "baixa": 0}
    if not cycle_path or not cycle_path.exists():
        return counts
    content = cycle_path.read_text(encoding="utf-8", errors="ignore")
    for line in content.splitlines():
        lower = line.lower()
        if re.search(r"\|\s*alta\s*\|", lower):
            counts["alta"] += 1
        elif re.search(r"\|\s*m[eé]dia\s*\|", lower):
            counts["media"] += 1
        elif re.search(r"\|\s*baixa\s*\|", lower):
            counts["baixa"] += 1
    return counts


def count_security_findings(security_path: Path) -> dict:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    if not security_path.exists():
        return counts
    content = security_path.read_text(encoding="utf-8", errors="ignore")
    for line in content.splitlines():
        lower = line.lower()
        if re.search(r"\|\s*(critical|cr[ií]tic[oa])\s*\|", lower):
            counts["critical"] += 1
        elif re.search(r"\|\s*(high|alt[oa])\s*\|", lower):
            counts["high"] += 1
        elif re.search(r"\|\s*(medium|m[eé]di[oa])\s*\|", lower):
            counts["medium"] += 1
        elif re.search(r"\|\s*(low|baix[oa])\s*\|", lower):
            counts["low"] += 1
    return counts


def determine_verdict(
    coverage: float | None,
    defects: dict,
    security: dict,
    threshold: float,
) -> str:
    if defects["alta"] > 0:
        return "NO-GO"
    if security["critical"] > 0:
        return "NO-GO"
    if coverage is not None and coverage < threshold:
        return "NO-GO"
    if defects["media"] > 0 or security["high"] > 0:
        return "GO COM RESSALVAS"
    return "GO"


def consolidate(output_folder: Path, threshold: float, verbose: bool = False) -> dict:
    reports_dir = output_folder / "reports"

    layer1_path = reports_dir / "verify-layer1-automated.md"
    cycle_path = find_latest_test_cycle(reports_dir)
    security_path = reports_dir / "security-report.md"

    missing = []
    if not layer1_path.exists():
        missing.append("verify-layer1-automated.md")
    if cycle_path is None:
        missing.append("test-cycle-N.md (no cycle reports found)")
    if not security_path.exists():
        missing.append("security-report.md")

    if missing:
        return {
            "script": "consolidate-results",
            "version": "1.0.0",
            "output_folder": str(output_folder),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "error",
            "findings": [
                {
                    "severity": "critical",
                    "category": "structure",
                    "location": {"file": str(reports_dir)},
                    "issue": f"Missing verification reports: {', '.join(missing)}",
                    "fix": "Ensure all verification layers complete before consolidation",
                }
            ],
            "summary": {
                "total": 1,
                "critical": 1,
                "high": 0,
                "medium": 0,
                "low": 0,
            },
        }

    coverage = extract_coverage(layer1_path)
    defects = count_defects_by_severity(cycle_path)
    security = count_security_findings(security_path)
    verdict = determine_verdict(coverage, defects, security, threshold)

    if verbose:
        print(f"Coverage: {coverage}%", file=sys.stderr)
        print(f"Defects: {defects}", file=sys.stderr)
        print(f"Security: {security}", file=sys.stderr)
        print(f"Verdict: {verdict}", file=sys.stderr)

    findings = []
    if defects["alta"] > 0:
        findings.append({
            "severity": "critical",
            "category": "functional",
            "location": {"file": str(cycle_path)},
            "issue": f"{defects['alta']} defeito(s) de severidade Alta",
            "fix": "Corrigir todos os defeitos Alta antes de prosseguir",
        })
    if security["critical"] > 0:
        findings.append({
            "severity": "critical",
            "category": "security",
            "location": {"file": str(security_path)},
            "issue": f"{security['critical']} vulnerabilidade(s) critica(s)",
            "fix": "Remediar todas as vulnerabilidades criticas",
        })
    if coverage is not None and coverage < threshold:
        findings.append({
            "severity": "critical",
            "category": "coverage",
            "location": {"file": str(layer1_path)},
            "issue": f"Cobertura {coverage}% abaixo do minimo {threshold}%",
            "fix": "Adicionar testes para atingir cobertura minima",
        })
    if defects["media"] > 0:
        findings.append({
            "severity": "high",
            "category": "functional",
            "location": {"file": str(cycle_path)},
            "issue": f"{defects['media']} defeito(s) de severidade Media",
            "fix": "Avaliar workarounds e documentar no relatorio",
        })
    if security["high"] > 0:
        findings.append({
            "severity": "high",
            "category": "security",
            "location": {"file": str(security_path)},
            "issue": f"{security['high']} vulnerabilidade(s) de severidade alta",
            "fix": "Planejar remediacao e documentar riscos aceitos",
        })

    return {
        "script": "consolidate-results",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if verdict == "NO-GO" else (
            "warning" if verdict == "GO COM RESSALVAS" else "pass"
        ),
        "verdict": verdict,
        "metrics": {
            "coverage_percent": coverage,
            "coverage_threshold": threshold,
            "defects_alta": defects["alta"],
            "defects_media": defects["media"],
            "defects_baixa": defects["baixa"],
            "security_critical": security["critical"],
            "security_high": security["high"],
            "security_medium": security["medium"],
            "security_low": security["low"],
        },
        "reports_analyzed": {
            "layer1": str(layer1_path),
            "test_cycle": str(cycle_path),
            "security": str(security_path),
        },
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": sum(1 for f in findings if f["severity"] == "critical"),
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate verification layer results into a Go/No-Go recommendation.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder containing reports/ directory",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=80.0,
        help="Minimum coverage percentage (default: 80.0)",
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

    result = consolidate(args.output_folder, args.threshold, verbose=args.verbose)

    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)

    exit_code = {"pass": 0, "warning": 0, "fail": 1, "error": 2}.get(
        result["status"], 2,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
