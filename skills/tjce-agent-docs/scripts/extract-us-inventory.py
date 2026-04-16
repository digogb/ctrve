#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Extract a structured User Story inventory from user-stories.md.

Parses US-NNN entries with their titles and identifies which ones
involve screen interaction (candidates for manual sections).

Usage:
    python3 extract-us-inventory.py user-stories.md
    python3 extract-us-inventory.py user-stories.md -o inventory.json

Exit codes:
    0 = extraction successful
    1 = no US found
    2 = file error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Heuristic: US that mention these terms likely involve screen interaction
_SCREEN_KEYWORDS = re.compile(
    r"(?:tela|formulario|pagina|campo|botao|clicar|preencher|selecionar|"
    r"visualizar|exibir|listar|consultar|cadastrar|buscar|filtrar|"
    r"acessar|menu|dialog|modal|alerta|mensagem|navegar|login|logout|"
    r"upload|download|relatorio|imprimir|exportar)",
    re.IGNORECASE,
)


def extract_stories(text: str) -> list[dict]:
    """Extract US-NNN entries with title and screen interaction flag."""
    stories: list[dict] = []
    # Match patterns like: US-001: Title, US-001 - Title, ### US-001 Title
    pattern = re.compile(
        r"^\s*(?:#{1,4}\s*)?(US-\d{3})\s*[:\-|—]\s*(.+?)$",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        us_id = m.group(1)
        title = m.group(2).strip().rstrip("|").strip()
        # Get surrounding context up to next US or heading for keyword scan
        start = m.end()
        next_us = re.search(r"\nUS-\d{3}", text[start:])
        end = start + next_us.start() if next_us else min(start + 500, len(text))
        context = text[start:end]
        has_screen = bool(_SCREEN_KEYWORDS.search(title + " " + context))
        stories.append({
            "id": us_id,
            "title": title,
            "has_screen_interaction": has_screen,
        })

    # Deduplicate by id, keeping first occurrence
    seen: set[str] = set()
    unique: list[dict] = []
    for s in stories:
        if s["id"] not in seen:
            seen.add(s["id"])
            unique.append(s)
    return sorted(unique, key=lambda x: x["id"])


def build_inventory(text: str) -> dict:
    """Build complete US inventory."""
    stories = extract_stories(text)
    with_screen = [s for s in stories if s["has_screen_interaction"]]
    return {
        "stories": stories,
        "summary": {
            "total": len(stories),
            "with_screen": len(with_screen),
            "without_screen": len(stories) - len(with_screen),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract User Story inventory from user-stories.md"
    )
    parser.add_argument("user_stories", help="Path to user-stories.md")
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    try:
        text = Path(args.user_stories).read_text(encoding="utf-8")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    inventory = build_inventory(text)

    if not inventory["stories"]:
        print("ERROR: No US-NNN entries found", file=sys.stderr)
        sys.exit(1)

    output = json.dumps(inventory, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        s = inventory["summary"]
        print(
            f"Extracted: {s['total']} US, {s['with_screen']} with screen",
            file=sys.stderr,
        )
    else:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
