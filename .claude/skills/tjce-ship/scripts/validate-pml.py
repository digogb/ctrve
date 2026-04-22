#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Validate PML structural integrity — no empty or placeholder sections."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

FORBIDDEN_PATTERNS = [
    re.compile(r"(?i)\bTODO\b"),
    re.compile(r"(?i)\ba definir\b"),
    re.compile(r"(?i)\bTBD\b"),
    re.compile(r"(?i)\bpendente\b"),
    re.compile(r"(?i)\bplaceholder\b"),
    re.compile(r"(?i)\b(preencher|completar)\b"),
]


def validate_pml(pml_path: Path) -> dict:
    findings = []

    if not pml_path.exists():
        findings.append({
            "severity": "critical",
            "category": "pml",
            "location": {"file": str(pml_path)},
            "issue": "PML.md nao encontrado",
            "fix": "Execute tjce-agent-release PML (Step 3)",
        })
        return _build_result(pml_path, "fail", findings, sections=[])

    content = pml_path.read_text(encoding="utf-8", errors="ignore")

    if not content.strip():
        findings.append({
            "severity": "critical",
            "category": "pml",
            "location": {"file": str(pml_path)},
            "issue": "PML.md esta vazio",
            "fix": "Re-execute tjce-agent-release PML (Step 3)",
        })
        return _build_result(pml_path, "fail", findings, sections=[])

    sections = _extract_sections(content)

    if not sections:
        findings.append({
            "severity": "critical",
            "category": "pml",
            "location": {"file": str(pml_path)},
            "issue": "PML.md nao contem secoes (H2/H3)",
            "fix": "Re-execute tjce-agent-release PML (Step 3)",
        })
        return _build_result(pml_path, "fail", findings, sections=[])

    for section in sections:
        body = section["body"].strip()
        if not body:
            findings.append({
                "severity": "critical",
                "category": "pml",
                "location": {"file": str(pml_path), "line": section["line"]},
                "issue": f"Secao vazia: '{section['title']}'",
                "fix": "Re-execute tjce-agent-release PML com contexto adequado",
            })
            continue

        for pattern in FORBIDDEN_PATTERNS:
            match = pattern.search(body)
            if match:
                findings.append({
                    "severity": "critical",
                    "category": "pml",
                    "location": {"file": str(pml_path), "line": section["line"]},
                    "issue": f"Secao '{section['title']}' contem placeholder: '{match.group()}'",
                    "fix": "Re-execute tjce-agent-release PML com contexto adequado",
                })
                break

    section_statuses = []
    for section in sections:
        has_issue = any(
            f["location"].get("line") == section["line"]
            for f in findings
        )
        section_statuses.append({
            "title": section["title"],
            "level": section["level"],
            "line": section["line"],
            "status": "fail" if has_issue else "pass",
        })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    status = "fail" if critical > 0 else "pass"
    return _build_result(pml_path, status, findings, sections=section_statuses)


def _extract_sections(content: str) -> list[dict]:
    sections = []
    lines = content.split("\n")
    current = None

    for i, line in enumerate(lines, 1):
        match = re.match(r"^(#{2,3})\s+(.+)$", line)
        if match:
            if current:
                current["body"] = "\n".join(current["_lines"])
                del current["_lines"]
                sections.append(current)
            current = {
                "title": match.group(2).strip(),
                "level": len(match.group(1)),
                "line": i,
                "_lines": [],
            }
        elif current:
            current["_lines"].append(line)

    if current:
        current["body"] = "\n".join(current["_lines"])
        del current["_lines"]
        sections.append(current)

    return sections


def _build_result(pml_path, status, findings, sections):
    critical = sum(1 for f in findings if f["severity"] == "critical")
    return {
        "script": "validate-pml",
        "version": "1.0.0",
        "pml_path": str(pml_path),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "sections": sections,
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
        description="Validate PML structural integrity.",
    )
    parser.add_argument(
        "pml_path",
        type=Path,
        help="Path to PML.md file",
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
        print(f"Validating PML: {args.pml_path}", file=sys.stderr)

    result = validate_pml(args.pml_path)

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
