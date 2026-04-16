#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Scan source code for hardcoded secrets, tokens, API keys, and credentials."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS: list[tuple[str, str]] = [
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{16,}["\']', "API key"),
    (r'(?i)(secret|secret[_-]?key)\s*[=:]\s*["\'][a-zA-Z0-9_\-]{16,}["\']', "Secret key"),
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\'][^"\']{4,}["\']', "Password"),
    (r'(?i)(token|access[_-]?token|auth[_-]?token)\s*[=:]\s*["\'][a-zA-Z0-9_\-\.]{16,}["\']', "Token"),
    (r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*["\']AKIA[A-Z0-9]{16}["\']', "AWS Access Key"),
    (r'(?i)(aws[_-]?secret[_-]?access[_-]?key)\s*[=:]\s*["\'][a-zA-Z0-9/+=]{40}["\']', "AWS Secret Key"),
    (r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{20,}', "Bearer token"),
    (r'(?i)(connection[_-]?string|database[_-]?url|db[_-]?url)\s*[=:]\s*["\'][^"\']{10,}["\']', "Connection string"),
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key"),
]

SKIP_NAMES = {
    ".env.example", ".env.sample", ".env.template",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
}

SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", ".venv", "venv",
    "dist", "build", ".next",
}

SCAN_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".json", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".conf", ".env", ".sh", ".sql",
    ".html", ".css", ".vue", ".svelte",
}


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    if path.name in SKIP_NAMES:
        return True
    if "fixture" in path.name.lower() or "mock" in path.name.lower():
        return True
    return False


def scan_file(file_path: Path) -> list[dict]:
    findings = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except (PermissionError, OSError):
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern, secret_type in SECRET_PATTERNS:
            if re.search(pattern, line):
                masked_line = line.strip()
                if len(masked_line) > 120:
                    masked_line = masked_line[:120] + "..."
                findings.append({
                    "severity": "critical",
                    "category": "secrets",
                    "location": {"file": str(file_path), "line": line_num},
                    "issue": f"Possible {secret_type} found in source code",
                    "fix": "Move to environment variable or secrets manager",
                    "evidence": masked_line,
                })
                break
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
        description="Scan source code for hardcoded secrets, tokens, API keys, and credentials.",
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
        "script": "scan-secrets",
        "version": "1.0.0",
        "directories": [str(d) for d in args.directories],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else "pass",
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
