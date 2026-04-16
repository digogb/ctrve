#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Validate that test-cases.md contains all required columns.

Parses the markdown table in test-cases.md and verifies that every
required column header is present and every row has non-empty values
for required fields.

Usage:
    python3 validate-test-cases-schema.py test-cases.md
    python3 validate-test-cases-schema.py test-cases.md --json

Exit codes:
    0 = schema valid
    1 = schema violations found
    2 = could not read or parse file
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_COLUMNS = {"ID", "Titulo", "RN", "Pre-condicao", "Passos", "Resultado Esperado", "Tipo"}
VALID_TYPES = {"unitario", "integracao", "e2e"}


def parse_table(text: str) -> tuple[list[str], list[dict[str, str]]]:
    """Parse a markdown table, return (headers, rows)."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip().startswith("|")
    ]
    if len(lines) < 2:
        return [], []

    # First line is headers
    headers = [h.strip() for h in lines[0].split("|") if h.strip()]

    # Skip separator line (line with ---)
    rows = []
    for line in lines[1:]:
        if re.match(r"^\|[\s\-|]+\|$", line):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip() != ""]
        if cells:
            row = {}
            for i, header in enumerate(headers):
                row[header] = cells[i] if i < len(cells) else ""
            rows.append(row)

    return headers, rows


def validate_schema(
    headers: list[str], rows: list[dict[str, str]]
) -> dict:
    """Validate table schema against required columns."""
    violations = []
    header_set = set(headers)

    # Check missing columns
    missing_cols = REQUIRED_COLUMNS - header_set
    if missing_cols:
        violations.append({
            "type": "missing_columns",
            "issue": f"Missing required columns: {', '.join(sorted(missing_cols))}",
        })

    # Check each row
    for i, row in enumerate(rows, start=1):
        row_id = row.get("ID", f"row-{i}")

        # Check empty required cells
        for col in REQUIRED_COLUMNS:
            if col in header_set:
                val = row.get(col, "").strip()
                if not val or val.upper() in ("TODO", "TBD", "???"):
                    violations.append({
                        "type": "empty_cell",
                        "row": row_id,
                        "column": col,
                        "issue": f"{row_id}: column '{col}' is empty or placeholder",
                    })

        # Check ID format
        id_val = row.get("ID", "")
        if id_val and not re.match(r"^CT-\d{3}$", id_val):
            violations.append({
                "type": "invalid_id",
                "row": row_id,
                "issue": f"{row_id}: ID '{id_val}' does not match CT-NNN format",
            })

        # Check Tipo values
        tipo = row.get("Tipo", "").strip().lower()
        if tipo and tipo not in VALID_TYPES:
            violations.append({
                "type": "invalid_type",
                "row": row_id,
                "issue": f"{row_id}: Tipo '{tipo}' is not valid (expected: {', '.join(sorted(VALID_TYPES))})",
            })

    return {
        "total_rows": len(rows),
        "columns_found": headers,
        "missing_columns": sorted(missing_cols) if missing_cols else [],
        "violations": violations,
        "valid": len(violations) == 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate test-cases.md schema"
    )
    parser.add_argument("test_cases", help="Path to test-cases.md")
    parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )
    args = parser.parse_args()

    try:
        text = Path(args.test_cases).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"error": str(e), "parsed": False}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    headers, rows = parse_table(text)
    if not headers:
        if args.json:
            print(
                json.dumps(
                    {"error": "No markdown table found in file", "parsed": False}
                )
            )
        else:
            print("ERROR: No markdown table found in file", file=sys.stderr)
        sys.exit(2)

    result = validate_schema(headers, rows)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(
            f"Schema: {result['total_rows']} test cases, "
            f"{len(result['columns_found'])} columns — {status}"
        )
        if result["missing_columns"]:
            print(f"\nMissing columns: {', '.join(result['missing_columns'])}")
        if result["violations"]:
            print(f"\nViolations ({len(result['violations'])}):")
            for v in result["violations"]:
                print(f"  {v['issue']}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
