#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Extract a structured message catalog from messages.md.

Parses MSG-NNN entries with their text and context, producing a compact
JSON inventory for the technical writer agent.

Usage:
    python3 extract-messages.py messages.md
    python3 extract-messages.py messages.md -o messages-catalog.json

Exit codes:
    0 = extraction successful
    1 = no messages found
    2 = file error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_messages(text: str) -> list[dict]:
    """Extract MSG-NNN entries from messages.md.

    Supports two formats:
      - Table rows: | MSG-001 | Texto da mensagem | Contexto |
      - Heading + body: ### MSG-001 — Texto \n Contexto...
    """
    messages: list[dict] = []
    seen: set[str] = set()

    # Table format: | MSG-NNN | text | context? |
    table_pattern = re.compile(
        r"\|\s*(MSG-\d{3})\s*\|\s*(.+?)\s*\|(?:\s*(.*?)\s*\|)?",
    )
    for m in table_pattern.finditer(text):
        msg_id = m.group(1)
        if msg_id in seen:
            continue
        seen.add(msg_id)
        msg_text = m.group(2).strip()
        context = m.group(3).strip() if m.group(3) else ""
        messages.append({
            "id": msg_id,
            "text": msg_text,
            "context": context,
        })

    # Heading format: ### MSG-NNN — Text or MSG-NNN: Text
    heading_pattern = re.compile(
        r"(?:^|\n)\s*(?:#{1,4}\s*)?(MSG-\d{3})\s*[:\-—|]\s*(.+?)(?:\n|$)"
    )
    for m in heading_pattern.finditer(text):
        msg_id = m.group(1)
        if msg_id in seen:
            continue
        seen.add(msg_id)
        msg_text = m.group(2).strip()
        # Grab next line as context hint
        start = m.end()
        next_lines = text[start:start + 200].strip().split("\n")
        context = next_lines[0].strip() if next_lines else ""
        # Skip if context looks like another MSG or heading
        if context.startswith(("#", "|", "MSG-")):
            context = ""
        messages.append({
            "id": msg_id,
            "text": msg_text,
            "context": context,
        })

    return sorted(messages, key=lambda x: x["id"])


def build_catalog(text: str) -> dict:
    """Build complete message catalog."""
    messages = extract_messages(text)
    return {
        "messages": messages,
        "summary": {
            "total": len(messages),
            "with_context": sum(1 for m in messages if m["context"]),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract message catalog from messages.md"
    )
    parser.add_argument("messages_md", help="Path to messages.md")
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    try:
        text = Path(args.messages_md).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    catalog = build_catalog(text)

    if not catalog["messages"]:
        print("ERROR: No MSG-NNN entries found", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(catalog, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        s = catalog["summary"]
        print(
            f"Extracted: {s['total']} messages, {s['with_context']} with context",
            file=sys.stderr,
        )
    else:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
