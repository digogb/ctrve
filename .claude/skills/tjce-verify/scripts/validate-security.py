#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Validate basic OWASP security patterns: SQL injection, CORS, input validation, auth."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SECURITY_CHECKS: list[dict] = [
    {
        "pattern": r'(?i)(execute|cursor\.execute|query|\.raw)\s*\(\s*f["\']',
        "category": "injection",
        "severity": "critical",
        "issue": "Possible SQL injection: f-string in query execution",
        "fix": "Use parameterized queries with placeholders",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)(execute|cursor\.execute|query)\s*\([^)]*%[^)]*%\s',
        "category": "injection",
        "severity": "critical",
        "issue": "Possible SQL injection: string formatting in query",
        "fix": "Use parameterized queries with placeholders",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)(execute|cursor\.execute|query)\s*\([^)]*\+\s*\w+',
        "category": "injection",
        "severity": "critical",
        "issue": "Possible SQL injection: string concatenation in query",
        "fix": "Use parameterized queries with placeholders",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?:SELECT|INSERT|UPDATE|DELETE|FROM|WHERE).*\$\{',
        "category": "injection",
        "severity": "critical",
        "issue": "Possible SQL injection: template literal in SQL query",
        "fix": "Use parameterized queries with placeholders",
        "extensions": {".js", ".ts", ".jsx", ".tsx"},
    },
    {
        "pattern": r'\$\{.*\}.*(?:SELECT|INSERT|UPDATE|DELETE|FROM|WHERE)',
        "category": "injection",
        "severity": "critical",
        "issue": "Possible SQL injection: template literal in SQL query",
        "fix": "Use parameterized queries with placeholders",
        "extensions": {".js", ".ts", ".jsx", ".tsx"},
    },
    {
        "pattern": r'(?i)(access-control-allow-origin|cors.*origin)\s*[=:]\s*["\']?\*["\']?',
        "category": "cors",
        "severity": "high",
        "issue": "CORS configured with wildcard origin (*)",
        "fix": "Restrict CORS to specific allowed origins",
        "extensions": {".py", ".js", ".ts", ".json", ".yaml", ".yml", ".conf"},
    },
    {
        "pattern": r'(?<!\w)(eval|exec)\s*\(',
        "category": "input_validation",
        "severity": "critical",
        "issue": "Use of eval/exec — potential code injection",
        "fix": "Replace with safe alternatives (json.loads, ast.literal_eval)",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)pickle\.loads?\s*\(',
        "category": "input_validation",
        "severity": "high",
        "issue": "Insecure deserialization via pickle",
        "fix": "Avoid pickle with untrusted data; use json or safe alternatives",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)yaml\.load\s*\([^)]*\)(?!.*Loader)',
        "category": "input_validation",
        "severity": "high",
        "issue": "Insecure YAML loading without safe Loader",
        "fix": "Use yaml.safe_load() instead",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)(jwt[_.]?secret|jwt[_.]?key)\s*[=:]\s*["\'][^"\']+["\']',
        "category": "auth",
        "severity": "critical",
        "issue": "Hardcoded JWT secret in source code",
        "fix": "Move JWT secret to environment variable",
        "extensions": {".py", ".js", ".ts", ".json", ".yaml", ".yml"},
    },
    {
        "pattern": r'(?i)verify\s*=\s*False',
        "category": "auth",
        "severity": "high",
        "issue": "SSL/TLS verification disabled",
        "fix": "Enable SSL verification; use proper certificates",
        "extensions": {".py"},
    },
    {
        "pattern": r'(?i)NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*["\']?0',
        "category": "auth",
        "severity": "high",
        "issue": "Node.js TLS verification disabled",
        "fix": "Remove NODE_TLS_REJECT_UNAUTHORIZED=0; use proper certificates",
        "extensions": {".js", ".ts", ".env"},
    },
]

SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", ".venv", "venv",
    "dist", "build", ".next", "migrations",
}

SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
    ".conf", ".env", ".sql",
}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    return False


def scan_file(file_path: Path) -> list[dict]:
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError):
        return findings

    for check in SECURITY_CHECKS:
        if file_path.suffix not in check["extensions"]:
            continue
        for line_num, line in enumerate(content.splitlines(), start=1):
            if re.search(check["pattern"], line):
                evidence = line.strip()
                if len(evidence) > 120:
                    evidence = evidence[:120] + "..."
                findings.append({
                    "severity": check["severity"],
                    "category": check["category"],
                    "location": {"file": str(file_path), "line": line_num},
                    "issue": check["issue"],
                    "fix": check["fix"],
                    "evidence": evidence,
                })
    return findings


def scan_directories(dirs: list[Path], verbose: bool = False) -> list[dict]:
    findings = []
    for directory in dirs:
        if not directory.exists():
            if verbose:
                print(f"Directory not found, skipping: {directory}", file=sys.stderr)
            continue
        for file_path in sorted(directory.rglob("*")):
            if not file_path.is_file():
                continue
            if should_skip(file_path):
                continue
            if file_path.suffix not in SCAN_EXTENSIONS:
                continue
            if verbose:
                print(f"Scanning: {file_path}", file=sys.stderr)
            findings.extend(scan_file(file_path))
    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Validate basic OWASP security patterns: SQL injection, CORS, input validation, auth.",
    )
    parser.add_argument(
        "directories",
        nargs="+",
        type=Path,
        help="Directories to scan (e.g., backend/ frontend/)",
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

    findings = scan_directories(args.directories, verbose=args.verbose)

    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")

    result = {
        "script": "validate-security",
        "version": "1.0.0",
        "directories": [str(d) for d in args.directories],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else ("warning" if high > 0 else "pass"),
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }

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
