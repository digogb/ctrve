#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# ///
"""
Extract Git commits and group them by user story (US-XXX).

Reads git log from a given ref (tag or SHA) to HEAD, parses commit messages
for US-NNN references, and optionally enriches with story titles from
user-stories.md. Outputs a structured JSON changelog.

Usage:
    python3 extract-git-changelog.py /path/to/repo
    python3 extract-git-changelog.py /path/to/repo --since v1.0.0
    python3 extract-git-changelog.py /path/to/repo --stories path/to/user-stories.md
    python3 extract-git-changelog.py /path/to/repo -o changelog.json

Exit codes:
    0 = extraction successful
    1 = no commits found in range
    2 = not a git repo or path error
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

_US_PATTERN = re.compile(r"US-\d{3,}")

_GIT_LOG_FORMAT = "%H%n%h%n%an%n%aI%n%s%x00"
_FIELD_SEP = "\x00"


def get_last_tag(repo: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=str(repo),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except OSError:
        pass
    return None


def parse_git_log(repo: Path, since: str | None) -> list[dict]:
    cmd = ["git", "log", f"--format={_GIT_LOG_FORMAT}"]
    if since:
        cmd.append(f"{since}..HEAD")
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(repo),
        )
    except OSError:
        return []

    if result.returncode != 0:
        return []

    commits: list[dict] = []
    raw = result.stdout.strip()
    if not raw:
        return commits

    for entry in raw.split(_FIELD_SEP):
        lines = entry.strip().splitlines()
        if len(lines) < 5:
            continue
        commits.append({
            "sha": lines[0],
            "sha_short": lines[1],
            "author": lines[2],
            "date": lines[3],
            "message": lines[4],
        })
    return commits


def extract_stories_from_spec(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    titles: dict[str, str] = {}
    current_us = None
    for line in text.splitlines():
        us_ids = _US_PATTERN.findall(line)
        if us_ids and line.strip().startswith("#"):
            current_us = us_ids[0]
            title = re.sub(r"^#+\s*", "", line).strip()
            title = re.sub(r"US-\d{3,}\s*[-—:]\s*", "", title).strip()
            titles[current_us] = title
        elif us_ids and current_us is None:
            for uid in us_ids:
                if uid not in titles:
                    titles[uid] = ""
    return titles


def group_commits(
    commits: list[dict], story_titles: dict[str, str]
) -> dict:
    stories: dict[str, dict] = defaultdict(
        lambda: {"title": "", "commits": []}
    )
    unmapped: list[dict] = []
    authors: set[str] = set()

    for commit in commits:
        authors.add(commit["author"])
        us_refs = _US_PATTERN.findall(commit["message"])
        if us_refs:
            for us_id in us_refs:
                stories[us_id]["commits"].append(commit)
                if not stories[us_id]["title"] and us_id in story_titles:
                    stories[us_id]["title"] = story_titles[us_id]
        else:
            unmapped.append(commit)

    stories_dict = {}
    for us_id in sorted(stories.keys()):
        stories_dict[us_id] = {
            "title": stories[us_id]["title"]
            or story_titles.get(us_id, ""),
            "commits": stories[us_id]["commits"],
        }

    mapped = sum(len(s["commits"]) for s in stories_dict.values())

    return {
        "stories": stories_dict,
        "unmapped": unmapped,
        "authors": sorted(authors),
        "stats": {
            "total": len(commits),
            "mapped": mapped,
            "unmapped": len(unmapped),
            "stories_count": len(stories_dict),
        },
    }


def build_changelog(
    repo: Path, since: str | None, stories_path: Path | None
) -> dict:
    commits = parse_git_log(repo, since)
    story_titles = (
        extract_stories_from_spec(stories_path) if stories_path else {}
    )
    grouped = group_commits(commits, story_titles)
    return {
        "since": since or "(all)",
        "until": "HEAD",
        "total_commits": len(commits),
        **grouped,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Extract Git commits grouped by user story"
    )
    parser.add_argument("repo", help="Path to Git repository root")
    parser.add_argument(
        "--since",
        help="Git ref to start from (tag or SHA). Default: last tag or first commit",
    )
    parser.add_argument(
        "--stories", help="Path to user-stories.md for title enrichment"
    )
    parser.add_argument("-o", "--output", help="Output JSON path (default: stdout)")
    args = parser.parse_args()

    repo = Path(args.repo)
    if not (repo / ".git").is_dir() and not repo.name == ".git":
        git_check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, cwd=str(repo),
        )
        if git_check.returncode != 0:
            print(
                json.dumps({"error": f"{args.repo} is not a git repository"}),
            )
            sys.exit(2)

    since = args.since
    if not since:
        since = get_last_tag(repo)

    stories_path = Path(args.stories) if args.stories else None
    changelog = build_changelog(repo, since, stories_path)

    if changelog["total_commits"] == 0:
        print(json.dumps({
            "error": "No commits found in range",
            "since": since or "(none)",
            "total_commits": 0,
        }))
        sys.exit(1)

    output = json.dumps(changelog, ensure_ascii=False, indent=2)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
        mapped_pct = round(
            changelog["stats"]["mapped"] / changelog["total_commits"] * 100
        )
        print(
            json.dumps({
                "written": args.output,
                "total_commits": changelog["total_commits"],
                "mapped_pct": mapped_pct,
                "stories_count": changelog["stats"]["stories_count"],
            }),
        )
    else:
        print(output)


if __name__ == "__main__":
    main()
