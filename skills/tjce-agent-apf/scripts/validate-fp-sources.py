#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Validate that every function in contagem-detalhada.md references at least
one existing User Story (US-NNN) or Business Rule (RN-NNN).

Parses the function tables in contagem-detalhada.md, extracts the "Fonte"
column, and checks every reference against the IDs present in
user-stories.md and business-rules.md. Reports orphan functions
(references to non-existent IDs) and sourceless functions (empty or
placeholder source column).

Usage:
    python3 validate-fp-sources.py contagem-detalhada.md user-stories.md business-rules.md
    python3 validate-fp-sources.py contagem-detalhada.md user-stories.md business-rules.md --json

Exit codes:
    0 = all functions properly sourced
    1 = orphan or sourceless functions found
    2 = could not read or parse input files
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_us_ids(text: str) -> set[str]:
    """Extract all US-NNN identifiers from user-stories.md."""
    return set(re.findall(r"US-\d{3}", text))


def extract_rn_ids(text: str) -> set[str]:
    """Extract all RN-NNN identifiers from business-rules.md."""
    return set(re.findall(r"RN-\d{3}", text))


def extract_functions(text: str) -> list[dict]:
    """Extract functions from contagem-detalhada.md tables.

    Returns a list of {id, name, type, sources} dicts. The source cell
    is parsed for US-NNN / RN-NNN references. The "id" is the first
    cell if it looks like FD-NNN or FT-NNN.
    """
    functions: list[dict] = []
    id_pattern = re.compile(r"^(FD|FT)-\d{3}$")
    ref_pattern = re.compile(r"(US-\d{3}|RN-\d{3})")

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        # Skip separator lines
        if re.match(r"^\|[\s\-|]+\|$", stripped):
            continue
        cells = [c.strip() for c in stripped.split("|")[1:-1]]
        if not cells:
            continue
        fid = cells[0]
        if not id_pattern.match(fid):
            continue  # header or non-function row
        # Last cell holds the sources (by convention)
        source_cell = cells[-1] if cells else ""
        sources = ref_pattern.findall(source_cell)
        # Name is second cell, type is third cell (by convention)
        name = cells[1] if len(cells) > 1 else ""
        ftype = cells[2] if len(cells) > 2 else ""
        functions.append({
            "id": fid,
            "name": name,
            "type": ftype,
            "source_cell": source_cell,
            "sources": sources,
        })
    return functions


def validate_sources(
    functions: list[dict],
    us_ids: set[str],
    rn_ids: set[str],
) -> dict:
    """Return validation result with sourceless and orphan function lists."""
    sourceless: list[dict] = []
    orphan: list[dict] = []
    valid_refs = us_ids | rn_ids

    for fn in functions:
        if not fn["sources"]:
            sourceless.append({
                "id": fn["id"],
                "name": fn["name"],
                "issue": "Funcao sem referencia US/RN declarada",
            })
            continue
        invalid = [s for s in fn["sources"] if s not in valid_refs]
        if invalid:
            orphan.append({
                "id": fn["id"],
                "name": fn["name"],
                "invalid_refs": invalid,
                "issue": f"Referencia a IDs inexistentes: {', '.join(invalid)}",
            })

    return {
        "total_functions": len(functions),
        "sourceless": sourceless,
        "orphan": orphan,
        "valid": len(sourceless) == 0 and len(orphan) == 0,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate APF function sources against US/RN IDs"
    )
    parser.add_argument("contagem", help="Path to contagem-detalhada.md")
    parser.add_argument("user_stories", help="Path to user-stories.md")
    parser.add_argument("business_rules", help="Path to business-rules.md")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    try:
        contagem_text = Path(args.contagem).read_text(encoding="utf-8")
        us_text = Path(args.user_stories).read_text(encoding="utf-8")
        rn_text = Path(args.business_rules).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        if args.json:
            print(json.dumps({"error": str(e), "parsed": False}))
        else:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    us_ids = extract_us_ids(us_text)
    rn_ids = extract_rn_ids(rn_text)
    functions = extract_functions(contagem_text)

    if not functions:
        if args.json:
            print(json.dumps({
                "error": "Nenhuma funcao encontrada em contagem-detalhada.md",
                "parsed": False,
            }))
        else:
            print(
                "ERROR: Nenhuma funcao (FD-NNN ou FT-NNN) encontrada.",
                file=sys.stderr,
            )
        sys.exit(2)

    result = validate_sources(functions, us_ids, rn_ids)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if result["valid"] else "FAIL"
        print(
            f"Fontes: {result['total_functions']} funcoes analisadas — {status}"
        )
        if result["sourceless"]:
            print(f"\nFuncoes sem fonte ({len(result['sourceless'])}):")
            for item in result["sourceless"]:
                print(f"  {item['id']} ({item['name']}): {item['issue']}")
        if result["orphan"]:
            print(f"\nFuncoes orfas ({len(result['orphan'])}):")
            for item in result["orphan"]:
                print(f"  {item['id']} ({item['name']}): {item['issue']}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
