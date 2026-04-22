#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Combine scan-secrets and validate-security JSON outputs into a markdown security report."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def format_markdown(secrets_data: dict, security_data: dict) -> str:
    ts = datetime.now(timezone.utc).isoformat()
    all_findings: list[dict] = []
    all_findings.extend(secrets_data.get("findings", []))
    all_findings.extend(security_data.get("findings", []))

    by_severity: dict[str, list[dict]] = {
        "critical": [], "high": [], "medium": [], "low": [],
    }
    for f in all_findings:
        sev = f.get("severity", "low")
        by_severity.setdefault(sev, []).append(f)

    total = len(all_findings)
    status = "PASS" if total == 0 else (
        "BLOQUEADO" if by_severity["critical"] else "ATENCAO"
    )

    lines = [
        f"# Security Report — {status}",
        "",
        f"**Data:** {ts}",
        f"**Total findings:** {total}",
        f"**Critical:** {len(by_severity['critical'])} | "
        f"**High:** {len(by_severity['high'])} | "
        f"**Medium:** {len(by_severity['medium'])} | "
        f"**Low:** {len(by_severity['low'])}",
        "",
    ]

    if not all_findings:
        lines.append("Nenhuma vulnerabilidade encontrada.")
        lines.append("")
        return "\n".join(lines)

    lines.append("## Findings")
    lines.append("")
    lines.append("| Severidade | Categoria | Arquivo | Linha | Issue | Fix |")
    lines.append("| ---------- | --------- | ------- | ----- | ----- | --- |")

    for sev in ["critical", "high", "medium", "low"]:
        for f in by_severity[sev]:
            loc = f.get("location", {})
            file_path = loc.get("file", "—")
            line = loc.get("line", "—")
            cat = f.get("category", "—")
            issue = f.get("issue", "—")
            fix = f.get("fix", "—")
            lines.append(f"| {sev} | {cat} | {file_path} | {line} | {issue} | {fix} |")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Combine scan-secrets and validate-security JSON outputs into markdown.",
    )
    parser.add_argument(
        "secrets_json",
        type=Path,
        help="Path to scan-secrets JSON output",
    )
    parser.add_argument(
        "security_json",
        type=Path,
        help="Path to validate-security JSON output",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Write markdown output to file instead of stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print diagnostic messages to stderr",
    )
    args = parser.parse_args()

    secrets_data = load_json(args.secrets_json)
    security_data = load_json(args.security_json)

    if secrets_data is None:
        print(f"Error: cannot read {args.secrets_json}", file=sys.stderr)
        sys.exit(2)
    if security_data is None:
        print(f"Error: cannot read {args.security_json}", file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        s_count = len(secrets_data.get("findings", []))
        v_count = len(security_data.get("findings", []))
        print(f"Secrets findings: {s_count}, Security findings: {v_count}", file=sys.stderr)

    markdown = format_markdown(secrets_data, security_data)

    if args.output:
        args.output.write_text(markdown, encoding="utf-8")
        if args.verbose:
            print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(markdown)

    has_critical = any(
        f.get("severity") == "critical"
        for f in secrets_data.get("findings", []) + security_data.get("findings", [])
    )
    sys.exit(1 if has_critical else 0)


if __name__ == "__main__":
    main()
