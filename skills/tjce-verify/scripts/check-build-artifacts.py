#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Check that required BUILD phase artifacts exist before VERIFY can proceed."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_ARTIFACTS = [
    "tests/test-cases.md",
    "reports/code-review.md",
    "reports/coverage-report.md",
]

OPTIONAL_ARTIFACTS = [
    "architecture/data-model.md",
]


def check_artifacts(output_folder: Path) -> dict:
    findings = []

    for artifact in REQUIRED_ARTIFACTS:
        path = output_folder / artifact
        if not path.exists():
            findings.append({
                "severity": "critical",
                "category": "structure",
                "location": {"file": str(path)},
                "issue": f"Required BUILD artifact missing: {artifact}",
                "fix": "Run tjce-agent-qa build to generate this artifact",
            })

    for artifact in OPTIONAL_ARTIFACTS:
        path = output_folder / artifact
        if not path.exists():
            findings.append({
                "severity": "info",
                "category": "structure",
                "location": {"file": str(path)},
                "issue": f"Optional artifact not found: {artifact}",
                "fix": "Not blocking — artifact is optional for verification",
            })

    critical = sum(1 for f in findings if f["severity"] == "critical")

    return {
        "script": "check-build-artifacts",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else "pass",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Check that required BUILD phase artifacts exist before VERIFY can proceed.",
    )
    parser.add_argument(
        "output_folder",
        type=Path,
        help="Path to the output folder (e.g., _bmad-output)",
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
        print(f"Checking artifacts in: {args.output_folder}", file=sys.stderr)

    result = check_artifacts(args.output_folder)

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
