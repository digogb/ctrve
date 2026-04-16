#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Validate RN → CT traceability between business-rules.md and test-cases.md.

Extracts all RN-NNN identifiers from business-rules.md and all RN references
from the test-cases.md table, then reports any RNs without test coverage.

Usage:
    python3 validate-traceability.py business-rules.md test-cases.md
    python3 validate-traceability.py business-rules.md test-cases.md --json

Exit codes:
    0 = all RNs have at least one test case
    1 = some RNs are uncovered
    2 = could not read or parse input files
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_rn_ids(text: str) -> list[str]:
    """Extract all RN-NNN identifiers from business-rules.md."""
    return sorted(set(re.findall(r"RN-\d{3}", text)))


def extract_ct_rn_refs(text: str) -> dict[str, list[str]]:
    """Extract CT → RN mappings from test-cases.md table rows."""
    # Match table rows: | CT-NNN | ... | RN-NNN, RN-NNN | ...
    ct_rn_map: dict[str, list[str]] = {}
    # Find all CT IDs and their associated RN references in the same row
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        ct_match = None
        rn_refs: list[str] = []
        for cell in cells:
            ct_found = re.findall(r"CT-\d{3}", cell)
            if ct_found:
                ct_match = ct_found[0]
            rn_found = re.findall(r"RN-\d{3}", cell)
            rn_refs.extend(rn_found)
        if ct_match and rn_refs:
            ct_rn_map[ct_match] = sorted(set(rn_refs))
    return ct_rn_map


def validate_traceability(
    rn_ids: list[str], ct_rn_map: dict[str, list[str]]
) -> dict:
    """Check that every RN has at least one CT covering it."""
    covered_rns: set[str] = set()
    for rn_list in ct_rn_map.values():
        covered_rns.update(rn_list)

    uncovered = [rn for rn in rn_ids if rn not in covered_rns]
    rn_to_cts: dict[str, list[str]] = {}
    for rn in rn_ids:
        rn_to_cts[rn] = [
            ct for ct, rns in ct_rn_map.items() if rn in rns
        ]

    return {
        "total_rn": len(rn_ids),
        "total_ct": len(ct_rn_map),
        "covered_rn": len(rn_ids) - len(uncovered),
        "uncovered_rn": uncovered,
        "coverage_pct": round(
            (len(rn_ids) - len(uncovered)) / len(rn_ids) * 100
            if rn_ids
            else 0,
            1,
        ),
        "rn_to_cts": rn_to_cts,
        "all_covered": len(uncovered) == 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate RN → CT traceability"
    )
    parser.add_argument(
        "business_rules", help="Path to business-rules.md"
    )
    parser.add_argument(
        "test_cases", help="Path to test-cases.md"
    )
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    args = parser.parse_args()

    try:
        br_text = Path(args.business_rules).read_text(encoding="utf-8")
        tc_text = Path(args.test_cases).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"error": str(e), "parsed": False}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    rn_ids = extract_rn_ids(br_text)
    if not rn_ids:
        if args.json:
            print(
                json.dumps(
                    {"error": "No RN-NNN found in business-rules.md", "parsed": False}
                )
            )
        else:
            print(
                "ERROR: No RN-NNN identifiers found in business-rules.md",
                file=sys.stderr,
            )
        sys.exit(2)

    ct_rn_map = extract_ct_rn_refs(tc_text)
    result = validate_traceability(rn_ids, ct_rn_map)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result["all_covered"] else "FAIL"
        print(
            f"Traceability: {result['covered_rn']}/{result['total_rn']} RNs covered "
            f"({result['coverage_pct']}%) — {status}"
        )
        print(f"Test cases: {result['total_ct']}")
        if result["uncovered_rn"]:
            print(f"\nUncovered RNs ({len(result['uncovered_rn'])}):")
            for rn in result["uncovered_rn"]:
                print(f"  {rn}")
            print(
                f"\nBLOCKING: {len(result['uncovered_rn'])} RN(s) have no test cases."
            )

    sys.exit(0 if result["all_covered"] else 1)


if __name__ == "__main__":
    main()
