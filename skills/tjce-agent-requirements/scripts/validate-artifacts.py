#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Post-processing validator for PDS Unificado requirement artifacts.

Runs deterministic checks that would otherwise consume ~2,500 LLM tokens per invocation:
- ID sequential validation (US-NNN, RN-NNN, MSG-NNN)
- Cross-reference integrity: RN → US, MSG → RN
- Message type coverage (erro, sucesso, validacao, confirmacao)
- Empty/placeholder cell detection
- N/A exception justification validation
- Traceability coverage counts

Usage:
    python3 validate-artifacts.py <artifacts-dir>
    python3 validate-artifacts.py <artifacts-dir> --json

Exit codes:
    0 = all checks pass
    1 = validation failures found
    2 = missing required files
"""

import argparse
import json
import re
import sys
from pathlib import Path

REQUIRED_FILES = ["user-stories.md", "business-rules.md", "messages.md", "product-vision.md"]
REQUIRED_MSG_TYPES = {"erro", "sucesso", "validacao", "confirmacao"}
FORBIDDEN_PATTERNS = re.compile(r"^\s*$|TODO|TBD|a definir|verificar posteriormente", re.IGNORECASE)
ID_PATTERNS = {
    "US": re.compile(r"US-(\d{3})"),
    "RN": re.compile(r"RN-(\d{3})"),
    "MSG": re.compile(r"MSG-(\d{3})"),
}


def parse_markdown_table(content: str) -> list[dict[str, str]]:
    """Extract rows from the first markdown table found in content."""
    lines = content.strip().split("\n")
    table_lines = []
    in_table = False
    headers = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            if not in_table:
                headers = [h.strip() for h in stripped.split("|")[1:-1]]
                in_table = True
            elif re.match(r"^\|[\s\-:|]+\|$", stripped):
                continue
            else:
                values = [v.strip() for v in stripped.split("|")[1:-1]]
                if len(values) == len(headers):
                    table_lines.append(dict(zip(headers, values)))
        elif in_table:
            break

    return table_lines


def extract_ids(content: str, prefix: str) -> list[int]:
    """Extract all IDs of a given prefix, return sorted list of numbers."""
    pattern = ID_PATTERNS[prefix]
    return sorted(int(m) for m in pattern.findall(content))


def extract_id_refs(cell: str, prefix: str) -> list[str]:
    """Extract all ID references from a table cell."""
    pattern = re.compile(rf"{prefix}-\d{{3}}")
    return pattern.findall(cell)


def check_sequential_ids(content: str, prefix: str) -> list[dict]:
    """Verify IDs are sequential starting from 001 with no gaps or duplicates."""
    violations = []
    ids = extract_ids(content, prefix)

    if not ids:
        return violations

    if ids[0] != 1:
        violations.append({
            "check": "sequential_ids",
            "prefix": prefix,
            "issue": f"{prefix}-001 missing, sequence starts at {prefix}-{ids[0]:03d}",
        })

    seen = set()
    for i, num in enumerate(ids):
        if num in seen:
            violations.append({
                "check": "sequential_ids",
                "prefix": prefix,
                "issue": f"Duplicate {prefix}-{num:03d}",
            })
        seen.add(num)

    for i in range(1, len(ids)):
        if ids[i] - ids[i - 1] > 1:
            for gap in range(ids[i - 1] + 1, ids[i]):
                violations.append({
                    "check": "sequential_ids",
                    "prefix": prefix,
                    "issue": f"Gap: {prefix}-{gap:03d} missing between {prefix}-{ids[i-1]:03d} and {prefix}-{ids[i]:03d}",
                })

    return violations


def check_cross_refs(source_rows: list[dict], source_col: str, target_ids: set[str], source_prefix: str, target_prefix: str, id_col: str) -> list[dict]:
    """Verify all references in source_col point to existing target IDs."""
    violations = []
    for row in source_rows:
        source_id = row.get(id_col, "?")
        refs = extract_id_refs(row.get(source_col, ""), target_prefix)
        if not refs:
            violations.append({
                "check": f"cross_ref_{source_prefix.lower()}_to_{target_prefix.lower()}",
                "entity": source_id,
                "issue": f"{source_id} has no {target_prefix} references in column '{source_col}'",
            })
        for ref in refs:
            if ref not in target_ids:
                violations.append({
                    "check": f"cross_ref_{source_prefix.lower()}_to_{target_prefix.lower()}",
                    "entity": source_id,
                    "issue": f"{source_id} references {ref} which does not exist",
                    "bad_ref": ref,
                })
    return violations


def check_msg_type_coverage(msg_rows: list[dict]) -> list[dict]:
    """Verify all four required message types are present."""
    violations = []
    found_types = {row.get("Tipo", "").strip().lower() for row in msg_rows}
    missing = REQUIRED_MSG_TYPES - found_types
    if missing:
        violations.append({
            "check": "msg_type_coverage",
            "issue": f"Missing message types: {', '.join(sorted(missing))}",
            "missing": sorted(missing),
        })
    invalid = found_types - REQUIRED_MSG_TYPES - {""}
    for t in invalid:
        violations.append({
            "check": "msg_type_coverage",
            "issue": f"Invalid message type: '{t}'. Valid types: erro, sucesso, validacao, confirmacao",
        })
    return violations


def check_empty_cells(rows: list[dict], file_name: str, id_col: str) -> list[dict]:
    """Check for empty cells or forbidden placeholder patterns in table rows."""
    violations = []
    for row in rows:
        entity_id = row.get(id_col, "?")
        for col, value in row.items():
            if FORBIDDEN_PATTERNS.match(value):
                violations.append({
                    "check": "empty_cells",
                    "file": file_name,
                    "entity": entity_id,
                    "column": col,
                    "value": value if value.strip() else "(empty)",
                    "issue": f"{entity_id} column '{col}' contains forbidden value: {value if value.strip() else '(empty)'}",
                })
    return violations


def check_na_justification(rn_rows: list[dict]) -> list[dict]:
    """Verify N/A in Excecao column has justification after dash."""
    violations = []
    na_pattern = re.compile(r"^N/A\s*$", re.IGNORECASE)
    na_justified = re.compile(r"^N/A\s*[—\-]\s*.+", re.IGNORECASE)

    for row in rn_rows:
        entity_id = row.get("ID", "?")
        excecao = row.get("Excecao", "").strip()
        if na_pattern.match(excecao):
            violations.append({
                "check": "na_justification",
                "entity": entity_id,
                "value": excecao,
                "issue": f"{entity_id} Excecao is 'N/A' without justification. Use 'N/A — {{motivo}}'",
            })
        elif excecao.upper().startswith("N/A") and not na_justified.match(excecao):
            violations.append({
                "check": "na_justification",
                "entity": entity_id,
                "value": excecao,
                "issue": f"{entity_id} Excecao starts with N/A but justification is missing or malformed",
            })
    return violations


def count_coverage(us_content: str, rn_rows: list[dict], msg_rows: list[dict]) -> dict:
    """Compute traceability coverage counts."""
    us_ids = {f"US-{n:03d}" for n in extract_ids(us_content, "US")}
    rn_ids = {row.get("ID", "") for row in rn_rows}
    msg_ids = {row.get("Codigo", "") for row in msg_rows}

    us_covered = set()
    for row in rn_rows:
        for ref in extract_id_refs(row.get("Estoria", ""), "US"):
            us_covered.add(ref)

    rn_covered = set()
    for row in msg_rows:
        for ref in extract_id_refs(row.get("Regra", ""), "RN"):
            rn_covered.add(ref)

    return {
        "total_us": len(us_ids),
        "total_rn": len(rn_ids),
        "total_msg": len(msg_ids),
        "us_with_rules": len(us_covered & us_ids),
        "rn_with_messages": len(rn_covered & rn_ids),
        "us_without_rules": sorted(us_ids - us_covered),
        "rn_without_messages": sorted(rn_ids - rn_covered),
    }


def main():
    parser = argparse.ArgumentParser(description="Validate PDS Unificado requirement artifacts")
    parser.add_argument("artifacts_dir", help="Path to the requirements directory")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    if not artifacts_dir.is_dir():
        print(f"Error: {artifacts_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    missing_files = [f for f in REQUIRED_FILES if not (artifacts_dir / f).exists()]
    if missing_files:
        if args.json:
            print(json.dumps({"valid": False, "error": "missing_files", "missing": missing_files}))
        else:
            print(f"Missing required files: {', '.join(missing_files)}", file=sys.stderr)
        sys.exit(2)

    us_content = (artifacts_dir / "user-stories.md").read_text(encoding="utf-8")
    rn_content = (artifacts_dir / "business-rules.md").read_text(encoding="utf-8")
    msg_content = (artifacts_dir / "messages.md").read_text(encoding="utf-8")

    rn_rows = parse_markdown_table(rn_content)
    msg_rows = parse_markdown_table(msg_content)

    us_id_set = {f"US-{n:03d}" for n in extract_ids(us_content, "US")}
    rn_id_set = {row.get("ID", "") for row in rn_rows}

    all_violations = []

    # SO-003: Sequential ID validation
    all_violations.extend(check_sequential_ids(us_content, "US"))
    all_violations.extend(check_sequential_ids(rn_content, "RN"))
    all_violations.extend(check_sequential_ids(msg_content, "MSG"))

    # SO-004: Cross-ref RN → US
    all_violations.extend(check_cross_refs(rn_rows, "Estoria", us_id_set, "RN", "US", "ID"))

    # SO-005: Cross-ref MSG → RN
    all_violations.extend(check_cross_refs(msg_rows, "Regra", rn_id_set, "MSG", "RN", "Codigo"))

    # SO-006: Message type coverage
    all_violations.extend(check_msg_type_coverage(msg_rows))

    # SO-007: Empty/placeholder cells
    all_violations.extend(check_empty_cells(rn_rows, "business-rules.md", "ID"))
    all_violations.extend(check_empty_cells(msg_rows, "messages.md", "Codigo"))

    # SO-011: N/A justification
    all_violations.extend(check_na_justification(rn_rows))

    # SO-008: Coverage counts
    coverage = count_coverage(us_content, rn_rows, msg_rows)

    result = {
        "valid": len(all_violations) == 0,
        "violations": all_violations,
        "violation_count": len(all_violations),
        "coverage": coverage,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if all_violations:
            print(f"FAIL — {len(all_violations)} violation(s) found:\n")
            for v in all_violations:
                print(f"  [{v['check']}] {v['issue']}")
            print()
        else:
            print("PASS — all checks passed.\n")

        print(f"Coverage: {coverage['total_us']} US, {coverage['total_rn']} RN, {coverage['total_msg']} MSG")
        print(f"  US with rules: {coverage['us_with_rules']}/{coverage['total_us']}")
        print(f"  RN with messages: {coverage['rn_with_messages']}/{coverage['total_rn']}")
        if coverage["us_without_rules"]:
            print(f"  US without rules: {', '.join(coverage['us_without_rules'])}")
        if coverage["rn_without_messages"]:
            print(f"  RN without messages: {', '.join(coverage['rn_without_messages'])}")

    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
