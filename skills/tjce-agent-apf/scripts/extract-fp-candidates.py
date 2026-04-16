#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Pre-pass: extract FP candidates from TJCE requirement artifacts.

Reads user-stories.md, business-rules.md, and data-model.md, then emits
a compact JSON inventory of candidate functions for the LLM to classify
without re-reading the source artifacts.

Extraction heuristics (deterministic, no judgment):
    - Entities from data-model.md tables/headings → candidate ALI/AIE
    - User stories (US-NNN) → candidate transactional function seeds
    - Business rules (RN-NNN) → mentioned to link sources

Usage:
    python3 extract-fp-candidates.py spec/ -o candidates.json
    python3 extract-fp-candidates.py --user-stories us.md --business-rules rn.md --data-model dm.md

Exit codes:
    0 = extraction successful
    1 = no artifacts found or empty
    2 = file error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_entities(data_model_text: str) -> list[dict]:
    """Extract entity candidates from data-model.md.

    Heuristic: level-2 or level-3 headings (## Entidade, ### Entidade) and
    top rows of entity tables are candidate entities. Returns list of
    {name, source_line} dicts.
    """
    entities: list[dict] = []
    seen: set[str] = set()

    for i, line in enumerate(data_model_text.splitlines(), start=1):
        stripped = line.strip()
        m = re.match(r"^#{2,3}\s+(.+?)\s*$", stripped)
        if m:
            name = m.group(1).strip()
            # Skip meta-headings
            if name.lower() in {
                "entidades", "relacionamentos", "modelo de dados",
                "overview", "visao geral", "indice",
            }:
                continue
            if name not in seen:
                seen.add(name)
                entities.append({"name": name, "source_line": i})
    return entities


def extract_user_stories(us_text: str) -> list[dict]:
    """Extract US-NNN candidates with their title line."""
    stories: list[dict] = []
    # Match US-NNN followed by optional separator and title until end of line
    pattern = re.compile(r"(US-\d{3})\s*[:\-|]\s*(.+?)(?:$|\|)", re.MULTILINE)
    for m in pattern.finditer(us_text):
        stories.append({"id": m.group(1), "title": m.group(2).strip()})
    # Also catch bare "US-NNN" identifiers without titles
    bare_ids = set(re.findall(r"US-\d{3}", us_text))
    captured = {s["id"] for s in stories}
    for sid in sorted(bare_ids - captured):
        stories.append({"id": sid, "title": ""})
    # Deduplicate by id, keeping titled version if present
    dedup: dict[str, dict] = {}
    for s in stories:
        if s["id"] not in dedup or s["title"]:
            dedup[s["id"]] = s
    return sorted(dedup.values(), key=lambda x: x["id"])


def extract_business_rules(rn_text: str) -> list[str]:
    """Extract RN-NNN identifiers."""
    return sorted(set(re.findall(r"RN-\d{3}", rn_text)))


def build_candidates(
    us_text: str, rn_text: str, dm_text: str
) -> dict:
    """Build a complete candidate inventory."""
    return {
        "entities": extract_entities(dm_text),
        "user_stories": extract_user_stories(us_text),
        "business_rules": extract_business_rules(rn_text),
        "summary": {
            "entity_count": len(extract_entities(dm_text)),
            "us_count": len(extract_user_stories(us_text)),
            "rn_count": len(extract_business_rules(rn_text)),
        },
    }


def resolve_paths(args) -> tuple[Path, Path, Path]:
    """Resolve paths from either --spec-dir or individual flags."""
    if args.spec_dir:
        base = Path(args.spec_dir)
        return (
            base / "user-stories.md",
            base / "business-rules.md",
            base.parent / "architecture" / "data-model.md"
            if (base.parent / "architecture" / "data-model.md").exists()
            else base / "data-model.md",
        )
    return (
        Path(args.user_stories),
        Path(args.business_rules),
        Path(args.data_model),
    )


def main():
    parser = argparse.ArgumentParser(
        description="Extract FP candidates from TJCE requirement artifacts"
    )
    parser.add_argument(
        "spec_dir", nargs="?",
        help="Path to directory containing user-stories.md and business-rules.md",
    )
    parser.add_argument("--user-stories", help="Path to user-stories.md")
    parser.add_argument("--business-rules", help="Path to business-rules.md")
    parser.add_argument("--data-model", help="Path to data-model.md")
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    if not args.spec_dir and not (
        args.user_stories and args.business_rules and args.data_model
    ):
        print(
            "ERROR: provide spec_dir or all three --user-stories/--business-rules/--data-model",
            file=sys.stderr,
        )
        sys.exit(1)

    us_path, rn_path, dm_path = resolve_paths(args)

    try:
        us_text = us_path.read_text(encoding="utf-8") if us_path.exists() else ""
        rn_text = rn_path.read_text(encoding="utf-8") if rn_path.exists() else ""
        dm_text = dm_path.read_text(encoding="utf-8") if dm_path.exists() else ""
    except OSError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if not us_text and not rn_text and not dm_text:
        print("ERROR: no artifact content found", file=sys.stderr)
        sys.exit(1)

    candidates = build_candidates(us_text, rn_text, dm_text)
    output = json.dumps(candidates, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Wrote: {args.output}", file=sys.stderr)
    else:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
