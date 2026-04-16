#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Parse coverage output from pytest-cov and Jest, extract metrics.

Reads coverage tool output (from stdin or file) and extracts:
- Total coverage percentage
- Per-module/file coverage breakdown
- Files below threshold
- Missing lines summary

Usage:
    python3 -m pytest --cov --cov-report=term-missing 2>&1 | python3 parse-coverage.py --threshold 80
    python3 parse-coverage.py coverage-output.txt --threshold 80
    python3 parse-coverage.py coverage-output.txt --threshold 80 --json

Exit codes:
    0 = coverage meets threshold
    1 = coverage below threshold
    2 = could not parse coverage output
"""

import argparse
import json
import re
import sys
from pathlib import Path


def parse_pytest_cov(text: str) -> dict | None:
    """Parse pytest-cov term-missing output."""
    # Match lines like: backend/app/main.py    45     3    93%   12-14
    # Or:               backend/app/main.py    45     3    93%
    pattern = re.compile(
        r"^(\S+\.py)\s+(\d+)\s+(\d+)\s+(\d+)%\s*(.*)?$", re.MULTILINE
    )
    matches = pattern.findall(text)
    if not matches:
        return None

    files = []
    total_stmts = 0
    total_miss = 0

    for match in matches:
        filepath, stmts, miss, cover, missing = match
        stmts_int = int(stmts)
        miss_int = int(miss)
        total_stmts += stmts_int
        total_miss += miss_int
        files.append({
            "file": filepath,
            "statements": stmts_int,
            "missing": miss_int,
            "coverage": int(cover),
            "missing_lines": missing.strip() if missing else "",
        })

    # Also try to find the TOTAL line
    total_pattern = re.compile(r"^TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", re.MULTILINE)
    total_match = total_pattern.search(text)
    if total_match:
        total_coverage = int(total_match.group(3))
    elif total_stmts > 0:
        total_coverage = round((total_stmts - total_miss) / total_stmts * 100)
    else:
        total_coverage = 0

    return {
        "tool": "pytest-cov",
        "total_coverage": total_coverage,
        "total_statements": total_stmts,
        "total_missing": total_miss,
        "files": files,
    }


def parse_jest_coverage(text: str) -> dict | None:
    """Parse Jest --coverage output."""
    # Match lines like: main.ts        |   85.71 |      100 |   66.67 |   85.71 | 15-20
    # Header:           File           | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
    pattern = re.compile(
        r"^\s*(\S+\.\w+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|[ \t]*(.*)?$",
        re.MULTILINE,
    )
    matches = pattern.findall(text)
    if not matches:
        return None

    files = []
    for match in matches:
        filepath, stmts, branch, funcs, lines, uncovered = match
        files.append({
            "file": filepath,
            "statements": float(stmts),
            "branches": float(branch),
            "functions": float(funcs),
            "lines": float(lines),
            "uncovered_lines": uncovered.strip() if uncovered else "",
        })

    # Find "All files" summary line
    all_files_pattern = re.compile(
        r"All files\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)",
    )
    all_match = all_files_pattern.search(text)
    if all_match:
        total_coverage = float(all_match.group(4))  # Use Lines %
    elif files:
        total_coverage = sum(f["lines"] for f in files) / len(files)
    else:
        total_coverage = 0.0

    return {
        "tool": "jest",
        "total_coverage": round(total_coverage, 2),
        "files": files,
    }


def parse_coverage(text: str) -> dict | None:
    """Try both parsers, return first that succeeds."""
    result = parse_pytest_cov(text)
    if result:
        return result
    result = parse_jest_coverage(text)
    if result:
        return result
    return None


def main():
    parser = argparse.ArgumentParser(description="Parse coverage tool output")
    parser.add_argument("input_file", nargs="?", help="Coverage output file (reads stdin if omitted)")
    parser.add_argument("--threshold", type=float, default=80.0, help="Minimum coverage threshold (default: 80)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input_file:
        text = Path(args.input_file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    result = parse_coverage(text)
    if result is None:
        if args.json:
            print(json.dumps({"error": "Could not parse coverage output", "parsed": False}))
        else:
            print("ERROR: Could not parse coverage output. Supported formats: pytest-cov (term-missing), Jest (--coverage)", file=sys.stderr)
        sys.exit(2)

    meets_threshold = result["total_coverage"] >= args.threshold
    result["threshold"] = args.threshold
    result["meets_threshold"] = meets_threshold

    below_threshold = []
    for f in result.get("files", []):
        cov = f.get("coverage", f.get("lines", 0))
        if cov < args.threshold:
            below_threshold.append({"file": f["file"], "coverage": cov})
    result["below_threshold"] = below_threshold

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        status = "PASS" if meets_threshold else "FAIL"
        print(f"Coverage: {result['total_coverage']}% (threshold: {args.threshold}%) — {status}")
        print(f"Tool: {result['tool']}")
        if below_threshold:
            print(f"\nFiles below {args.threshold}%:")
            for f in below_threshold:
                print(f"  {f['file']}: {f['coverage']}%")
        if not meets_threshold:
            print(f"\nBLOCKING: Coverage {result['total_coverage']}% is below {args.threshold}% threshold.")

    sys.exit(0 if meets_threshold else 1)


if __name__ == "__main__":
    main()
