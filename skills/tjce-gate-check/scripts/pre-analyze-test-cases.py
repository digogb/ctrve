#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Pre-analyze test cases structurally before LLM quality assessment."""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

CT_HEADER = re.compile(r"^##\s+(CT[-_]\d{3})\b", re.IGNORECASE)
RN_REF = re.compile(r"\bRN[-_]\d{3}\b")
EXPECTED_KEYWORDS = re.compile(
    r"(?i)\b(?:resultado\s+esperado|expected|espera-se|deve\s+retornar|deve\s+exibir|deve\s+apresentar)\b"
)


def analyze_test_cases(output_folder: Path) -> dict:
    path = output_folder / "tests" / "test-cases.md"
    findings = []

    if not path.exists():
        return _result(output_folder, findings, ct_count=0)

    content = path.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")

    ct_blocks = []
    current_ct = None

    for i, line in enumerate(lines):
        match = CT_HEADER.match(line)
        if match:
            if current_ct:
                current_ct["end"] = i
                ct_blocks.append(current_ct)
            current_ct = {"id": match.group(1).upper().replace("_", "-"), "start": i, "line": i + 1}
        elif current_ct and line.startswith("# "):
            current_ct["end"] = i
            ct_blocks.append(current_ct)
            current_ct = None

    if current_ct:
        current_ct["end"] = len(lines)
        ct_blocks.append(current_ct)

    for ct in ct_blocks:
        block_text = "\n".join(lines[ct["start"]:ct["end"]])

        if not RN_REF.search(block_text):
            findings.append({
                "severity": "high",
                "category": "test-quality",
                "location": {"file": str(path), "line": ct["line"]},
                "issue": f"{ct['id']} nao referencia nenhuma RN",
                "fix": f"Vincule {ct['id']} a pelo menos uma regra de negocio",
            })

        if not EXPECTED_KEYWORDS.search(block_text):
            findings.append({
                "severity": "medium",
                "category": "test-quality",
                "location": {"file": str(path), "line": ct["line"]},
                "issue": f"{ct['id']} sem indicador de resultado esperado",
                "fix": f"Adicione secao 'Resultado Esperado' com criterio verificavel",
                "needs_llm_review": True,
            })

        body = "\n".join(lines[ct["start"] + 1:ct["end"]]).strip()
        if len(body) < 30:
            findings.append({
                "severity": "high",
                "category": "test-quality",
                "location": {"file": str(path), "line": ct["line"]},
                "issue": f"{ct['id']} corpo muito curto ({len(body)} chars)",
                "fix": f"Expanda {ct['id']} com pre-condicoes, passos e resultado esperado",
            })

    return _result(output_folder, findings, ct_count=len(ct_blocks))


def _result(output_folder: Path, findings: list, ct_count: int) -> dict:
    return {
        "script": "pre-analyze-test-cases",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ct_count": ct_count,
        "needs_llm_review": [f for f in findings if f.get("needs_llm_review")],
        "status": "fail" if any(f["severity"] in ("critical", "high") for f in findings) else "pass",
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": 0,
            "high": sum(1 for f in findings if f["severity"] == "high"),
            "medium": sum(1 for f in findings if f["severity"] == "medium"),
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Pre-analyze test cases structurally before LLM review.",
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
        print(f"Pre-analyzing test cases in: {args.output_folder}", file=sys.stderr)

    result = analyze_test_cases(args.output_folder)

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
