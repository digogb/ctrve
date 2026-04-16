#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Validate manual-usuario.md coverage and terminology compliance.

Checks three dimensions:
  (a) Every US from user-stories.md with screen interaction has a section
  (b) Every message from messages.md appears in the manual
  (c) No prohibited technical jargon is present

Usage:
    python3 validate-manual.py manual-usuario.md user-stories.md messages.md
    python3 validate-manual.py manual-usuario.md user-stories.md messages.md --json

Exit codes:
    0 = all checks pass
    1 = coverage gaps or jargon found
    2 = file not found or parse error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PROHIBITED_TERMS = [
    "api", "endpoint", "query", "schema", "frontend", "backend",
    "request", "response", "payload", "json", "token", "middleware",
    "componente", "rota", "render", "state", "hook", "prop", "callback",
    "deploy", "commit", "branch", "merge", "pull request", "push",
    "database", "sql", "orm", "migration", "seed",
]

# Regex: match whole words only, case-insensitive
_JARGON_PATTERNS = [
    re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
    for term in PROHIBITED_TERMS
]


def extract_us_ids(text: str) -> list[str]:
    """Extract US-NNN identifiers from user-stories.md."""
    return sorted(set(re.findall(r"US-\d{3}", text)))


def extract_msg_ids(text: str) -> list[str]:
    """Extract MSG-NNN identifiers from messages.md."""
    return sorted(set(re.findall(r"MSG-\d{3}", text)))


def check_us_coverage(manual_text: str, us_ids: list[str]) -> dict:
    """Check that each US has a corresponding section in the manual."""
    covered = []
    uncovered = []
    for us_id in us_ids:
        if us_id in manual_text:
            covered.append(us_id)
        else:
            uncovered.append(us_id)
    return {
        "total": len(us_ids),
        "covered": len(covered),
        "uncovered": uncovered,
        "coverage_pct": round(
            len(covered) / len(us_ids) * 100 if us_ids else 0, 1
        ),
    }


def check_msg_coverage(manual_text: str, msg_ids: list[str]) -> dict:
    """Check that each message ID is referenced in the manual."""
    covered = []
    uncovered = []
    for msg_id in msg_ids:
        if msg_id in manual_text:
            covered.append(msg_id)
        else:
            uncovered.append(msg_id)
    return {
        "total": len(msg_ids),
        "covered": len(covered),
        "uncovered": uncovered,
        "coverage_pct": round(
            len(covered) / len(msg_ids) * 100 if msg_ids else 0, 1
        ),
    }


def check_jargon(manual_text: str) -> list[dict]:
    """Find prohibited technical terms in the manual."""
    findings: list[dict] = []
    for i, line in enumerate(manual_text.splitlines(), start=1):
        for pattern in _JARGON_PATTERNS:
            for match in pattern.finditer(line):
                findings.append({
                    "line": i,
                    "term": match.group().lower(),
                    "context": line.strip()[:120],
                })
    # Deduplicate by (line, term)
    seen: set[tuple[int, str]] = set()
    unique: list[dict] = []
    for f in findings:
        key = (f["line"], f["term"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def validate(
    manual_text: str, us_ids: list[str], msg_ids: list[str]
) -> dict:
    """Run all validations and return combined result."""
    us_cov = check_us_coverage(manual_text, us_ids)
    msg_cov = check_msg_coverage(manual_text, msg_ids)
    jargon = check_jargon(manual_text)

    valid = (
        len(us_cov["uncovered"]) == 0
        and len(msg_cov["uncovered"]) == 0
        and len(jargon) == 0
    )

    return {
        "us_coverage": us_cov,
        "msg_coverage": msg_cov,
        "jargon_findings": jargon,
        "jargon_count": len(jargon),
        "valid": valid,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate manual-usuario.md coverage and terminology"
    )
    parser.add_argument("manual", help="Path to manual-usuario.md")
    parser.add_argument("user_stories", help="Path to user-stories.md")
    parser.add_argument("messages", help="Path to messages.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        manual_text = Path(args.manual).read_text(encoding="utf-8")
        us_text = Path(args.user_stories).read_text(encoding="utf-8")
        msg_text = Path(args.messages).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"error": str(e), "parsed": False}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    us_ids = extract_us_ids(us_text)
    msg_ids = extract_msg_ids(msg_text)
    result = validate(manual_text, us_ids, msg_ids)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        us = result["us_coverage"]
        msg = result["msg_coverage"]
        status = "PASS" if result["valid"] else "FAIL"
        print(f"Manual Validation — {status}")
        print(
            f"  US coverage: {us['covered']}/{us['total']} "
            f"({us['coverage_pct']}%)"
        )
        if us["uncovered"]:
            print(f"    Uncovered: {', '.join(us['uncovered'])}")
        print(
            f"  MSG coverage: {msg['covered']}/{msg['total']} "
            f"({msg['coverage_pct']}%)"
        )
        if msg["uncovered"]:
            print(f"    Uncovered: {', '.join(msg['uncovered'])}")
        print(f"  Jargon findings: {result['jargon_count']}")
        if result["jargon_findings"]:
            for f in result["jargon_findings"][:10]:
                print(f"    L{f['line']}: \"{f['term']}\" — {f['context']}")
            if len(result["jargon_findings"]) > 10:
                print(
                    f"    ... and {len(result['jargon_findings']) - 10} more"
                )

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
