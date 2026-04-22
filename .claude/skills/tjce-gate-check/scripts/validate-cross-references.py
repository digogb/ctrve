#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Layer 2: Validate cross-references between SPEC artifacts (US, RN, MSG, CT IDs)."""

import argparse
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ID_PATTERNS = {
    "US": re.compile(r"\bUS[-_](\d{3})\b"),
    "RN": re.compile(r"\bRN[-_](\d{3})\b"),
    "MSG": re.compile(r"\bMSG[-_](\d{3})\b"),
    "CT": re.compile(r"\bCT[-_](\d{3})\b"),
}

ARTIFACT_FILES = {
    "user-stories": "requirements/user-stories.md",
    "business-rules": "requirements/business-rules.md",
    "messages": "requirements/messages.md",
    "test-cases": "tests/test-cases.md",
}

EXPECTED_DEFINITIONS = {
    "user-stories": "US",
    "business-rules": "RN",
    "messages": "MSG",
    "test-cases": "CT",
}

REQUIRED_LINKS = [
    ("RN", "US", "business-rules", "Toda RN deve vincular a pelo menos 1 US"),
    ("MSG", "RN", "messages", "Toda MSG deve vincular a pelo menos 1 RN"),
    ("CT", "RN", "test-cases", "Todo CT deve vincular a pelo menos 1 RN"),
]


def validate_cross_references(output_folder: Path) -> dict:
    findings = []

    defined_ids: dict[str, set[str]] = defaultdict(set)
    definition_counts: dict[str, int] = defaultdict(int)
    referenced_ids: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))

    for artifact_key, rel_path in ARTIFACT_FILES.items():
        path = output_folder / rel_path
        if not path.exists():
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        expected_prefix = EXPECTED_DEFINITIONS.get(artifact_key)

        for prefix, pattern in ID_PATTERNS.items():
            for match in pattern.finditer(content):
                full_id = f"{prefix}-{match.group(1)}"
                if prefix == expected_prefix:
                    defined_ids[prefix].add(full_id)
                    definition_counts[full_id] += 1
                referenced_ids[artifact_key][prefix].add(full_id)

    for source_prefix, target_prefix, source_file, rule in REQUIRED_LINKS:
        source_ids = defined_ids.get(source_prefix, set())
        refs_in_source = referenced_ids.get(source_file, {}).get(target_prefix, set())

        for sid in sorted(source_ids):
            path = output_folder / ARTIFACT_FILES[source_file]
            content = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
            sid_pattern = re.compile(re.escape(sid))
            sid_lines = [
                i + 1 for i, line in enumerate(content.split("\n"))
                if sid_pattern.search(line)
            ]

            has_link = False
            if sid_lines:
                for line_num in sid_lines:
                    context_start = max(0, line_num - 3)
                    context_end = min(len(content.split("\n")), line_num + 3)
                    context = "\n".join(content.split("\n")[context_start:context_end])
                    if ID_PATTERNS[target_prefix].search(context):
                        has_link = True
                        break

            if not has_link:
                findings.append({
                    "severity": "high",
                    "category": "cross-reference",
                    "location": {"file": str(output_folder / ARTIFACT_FILES[source_file])},
                    "issue": f"{sid} nao vincula a nenhum {target_prefix}: {rule}",
                    "fix": f"Adicione referencia a {target_prefix} no contexto de {sid}",
                })

    for full_id, count in sorted(definition_counts.items()):
        if count > 1:
            prefix = full_id.split("-")[0]
            source_file = [k for k, v in EXPECTED_DEFINITIONS.items() if v == prefix][0]
            findings.append({
                "severity": "high",
                "category": "duplicate-id",
                "location": {"file": str(output_folder / ARTIFACT_FILES[source_file])},
                "issue": f"ID duplicado: {full_id} definido {count} vezes",
                "fix": f"Remova definicoes duplicadas de {full_id}",
            })

    all_referenced = set()
    for artifact_refs in referenced_ids.values():
        for prefix_refs in artifact_refs.values():
            all_referenced.update(prefix_refs)

    all_defined = set()
    for ids in defined_ids.values():
        all_defined.update(ids)

    orphans = all_referenced - all_defined
    for orphan in sorted(orphans):
        for artifact_key, artifact_refs in referenced_ids.items():
            for prefix, refs in artifact_refs.items():
                if orphan in refs and orphan not in defined_ids.get(prefix, set()):
                    findings.append({
                        "severity": "low",
                        "category": "orphan-id",
                        "location": {"file": str(output_folder / ARTIFACT_FILES[artifact_key])},
                        "issue": f"ID orfao: {orphan} referenciado mas nao definido",
                        "fix": f"Verifique se {orphan} existe no artefato de origem ou corrija a referencia",
                    })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    high = sum(1 for f in findings if f["severity"] == "high")
    medium = sum(1 for f in findings if f["severity"] == "medium")
    return {
        "script": "validate-cross-references",
        "version": "1.0.0",
        "output_folder": str(output_folder),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "fail" if critical > 0 else ("warning" if high > 0 or medium > 0 else "pass"),
        "defined_ids": {k: sorted(v) for k, v in defined_ids.items()},
        "findings": findings,
        "summary": {
            "total": len(findings),
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": sum(1 for f in findings if f["severity"] == "low"),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate cross-references between SPEC artifacts.",
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
        print(f"Validating cross-references in: {args.output_folder}", file=sys.stderr)

    result = validate_cross_references(args.output_folder)

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
