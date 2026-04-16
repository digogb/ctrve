#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Extract screen metadata from a React/Next.js frontend codebase.

Scans JSX/TSX files for routes, component names, form labels, button texts,
placeholders, and help texts. Outputs a compact JSON inventory for the
technical writer agent, eliminating the need to re-read raw source.

Usage:
    python3 extract-screens.py /path/to/frontend/src
    python3 extract-screens.py /path/to/frontend/src -o screens.json
    python3 extract-screens.py /path/to/frontend/src --json

Exit codes:
    0 = extraction successful
    1 = no relevant files found
    2 = path error
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Patterns for metadata extraction
_ROUTE_PATTERNS = [
    # React Router: path="/something" or path: "/something"
    re.compile(r"""(?:path\s*[:=]\s*["'])(/[^"']*?)["']"""),
    # Next.js pages directory structure (captured from file paths)
]

_COMPONENT_PATTERN = re.compile(
    r"""(?:export\s+(?:default\s+)?(?:function|const)\s+|function\s+)"""
    r"""([A-Z][a-zA-Z0-9]+)""",
)

_LABEL_PATTERN = re.compile(
    r"""(?:label\s*[:=]\s*["']|<label[^>]*>)([^"'<]{2,60})""",
)

_BUTTON_PATTERN = re.compile(
    r"""<(?:Button|button)[^>]*>([^<]{2,60})</""",
)

_PLACEHOLDER_PATTERN = re.compile(
    r"""placeholder\s*[:=]\s*["']([^"']{2,80})["']""",
)

_HELP_TEXT_PATTERN = re.compile(
    r"""(?:helpText|helperText|description|title)\s*[:=]\s*["']([^"']{2,120})["']""",
)

_HEADING_PATTERN = re.compile(
    r"""<[hH][1-6][^>]*>([^<]{2,80})</[hH][1-6]>""",
)

# File extensions to scan
_EXTENSIONS = {".jsx", ".tsx", ".js", ".ts"}

# Directories to skip
_SKIP_DIRS = {
    "node_modules", ".next", "dist", "build", "__tests__",
    "__mocks__", ".git", "coverage",
}


def scan_file(file_path: Path) -> dict | None:
    """Extract screen metadata from a single file."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    components = _COMPONENT_PATTERN.findall(content)
    if not components:
        return None

    routes = _ROUTE_PATTERNS[0].findall(content)
    labels = _LABEL_PATTERN.findall(content)
    buttons = _BUTTON_PATTERN.findall(content)
    placeholders = _PLACEHOLDER_PATTERN.findall(content)
    help_texts = _HELP_TEXT_PATTERN.findall(content)
    headings = _HEADING_PATTERN.findall(content)

    # Skip pure utility/hook files with no UI indicators
    has_ui = labels or buttons or placeholders or headings or routes
    if not has_ui:
        return None

    return {
        "file": str(file_path),
        "components": sorted(set(components)),
        "routes": sorted(set(routes)) if routes else [],
        "labels": sorted(set(labels)),
        "buttons": sorted(set(buttons)),
        "placeholders": sorted(set(placeholders)),
        "help_texts": sorted(set(help_texts)),
        "headings": sorted(set(headings)),
    }


def scan_directory(root: Path) -> list[dict]:
    """Recursively scan a frontend source directory."""
    screens: list[dict] = []

    if not root.is_dir():
        return screens

    for file_path in sorted(root.rglob("*")):
        # Skip unwanted directories
        if any(skip in file_path.parts for skip in _SKIP_DIRS):
            continue
        if file_path.suffix not in _EXTENSIONS:
            continue
        if file_path.name.startswith("test") or file_path.name.endswith(".test.tsx"):
            continue

        result = scan_file(file_path)
        if result:
            screens.append(result)

    return screens


def extract_nextjs_routes(root: Path) -> list[dict]:
    """Extract routes from Next.js pages/app directory structure."""
    routes: list[dict] = []
    for pages_dir in ["pages", "app"]:
        pages_path = root / pages_dir
        if not pages_path.is_dir():
            continue
        for file_path in sorted(pages_path.rglob("*")):
            if file_path.suffix not in _EXTENSIONS:
                continue
            if file_path.name.startswith("_") or file_path.name.startswith("layout"):
                continue
            # Convert file path to route
            rel = file_path.relative_to(pages_path)
            route = "/" + str(rel.with_suffix("")).replace("\\", "/")
            route = route.replace("/index", "")
            if not route:
                route = "/"
            # [param] → :param
            route = re.sub(r"\[([^\]]+)\]", r":\1", route)
            routes.append({
                "route": route,
                "file": str(file_path),
                "page_component": file_path.stem.replace("-", " ").title().replace(" ", ""),
            })
    return routes


def build_inventory(root: Path) -> dict:
    """Build complete screen inventory."""
    screens = scan_directory(root)
    nextjs_routes = extract_nextjs_routes(root)

    # Deduplicate routes from both sources
    all_routes: set[str] = set()
    for s in screens:
        all_routes.update(s.get("routes", []))
    for r in nextjs_routes:
        all_routes.add(r["route"])

    return {
        "source_root": str(root),
        "screens": screens,
        "nextjs_routes": nextjs_routes,
        "summary": {
            "total_screen_files": len(screens),
            "total_routes": len(all_routes),
            "total_components": sum(
                len(s["components"]) for s in screens
            ),
            "total_labels": sum(len(s["labels"]) for s in screens),
            "total_buttons": sum(len(s["buttons"]) for s in screens),
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract screen metadata from React/Next.js frontend"
    )
    parser.add_argument(
        "source_dir", help="Path to frontend source directory (e.g., frontend/src)"
    )
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Force JSON output")
    args = parser.parse_args()

    root = Path(args.source_dir)
    if not root.is_dir():
        print(f"ERROR: {args.source_dir} is not a directory", file=sys.stderr)
        sys.exit(2)

    inventory = build_inventory(root)

    if not inventory["screens"] and not inventory["nextjs_routes"]:
        print(
            "ERROR: No screen files found. Verify the path points to "
            "a React/Next.js source directory.",
            file=sys.stderr,
        )
        sys.exit(1)

    output = json.dumps(inventory, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(
            f"Extracted: {inventory['summary']['total_screen_files']} screens, "
            f"{inventory['summary']['total_routes']} routes, "
            f"{inventory['summary']['total_labels']} labels",
            file=sys.stderr,
        )
    else:
        print(output)

    sys.exit(0)


if __name__ == "__main__":
    main()
