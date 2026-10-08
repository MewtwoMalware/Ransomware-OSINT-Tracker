#!/usr/bin/env python3

"""
Ransomware OSINT Tracker - Victim Counter

Scans ransomware Markdown files and generates victim statistics.
"""

from pathlib import Path
import json
import re
from collections import defaultdict
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"

VICTIM_COUNTS_FILE = DATA_DIR / "victim_counts.json"
VICTIMS_FILE = DATA_DIR / "victims.json"


IGNORE_FILES = {
    "README.md",
}

IGNORE_DIRS = {
    ".git",
    ".github",
    "data",
    "scripts",
    "node_modules",
}


def normalize_name(name):
    """Normalize an organization name for duplicate detection."""

    name = name.strip().lower()

    name = re.sub(r"[^\w\s]", "", name)

    name = re.sub(r"\s+", " ", name)

    suffixes = [
        " corporation",
        " corp",
        " incorporated",
        " inc",
        " limited",
        " ltd",
        " llc",
        " plc",
        " company",
        " co",
    ]

    for suffix in suffixes:
        if name.endswith(suffix):
            name = name[:-len(suffix)].strip()

    return name


def clean_victim_name(name):
    """Clean extracted victim text."""

    name = name.strip()

    name = re.sub(r"[*_`]", "", name)

    name = name.rstrip(".,;:")

    return name


def is_probable_victim(name):
    """Filter obvious non-victim text."""

    if not name:
        return False

    if len(name) < 3:
        return False

    ignored = {
        "ransomware",
        "victim",
        "victims",
        "company",
        "organization",
        "organisation",
        "group",
        "government",
        "researchers",
        "researcher",
        "security",
        "law enforcement",
        "unknown",
    }

    if name.lower() in ignored:
        return False

    return True


def find_markdown_files():
    """Find ransomware Markdown files in the repository."""

    files = []

    for path in ROOT_DIR.rglob("*.md"):

        if any(part in IGNORE_DIRS for part in path.parts):
            continue

        if path.name in IGNORE_FILES:
            continue

        files.append(path)

    return sorted(files)


def get_group_name(path):
    """Extract ransomware group name from the first Markdown heading."""

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )
    except Exception:
        return path.stem

    match = re.search(
        r"^#\s+(.+?)\s*$",
        content,
        re.MULTILINE
    )

    if match:
        return match.group(1).strip()

    return path.stem


def extract_victims_from_markdown(path):
    """
    Extract candidate victims.

    Currently supports:

    |Source|Date|Victim|Details|
    """

    content = path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    victims = []

    table_pattern = re.compile(
        r"^\s*\|?\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|?\s*$",
        re.MULTILINE
    )

    for match in table_pattern.finditer(content):

        source = match.group(1).strip()
        date = match.group(2).strip()
        victim = match.group(3).strip()
        details = match.group(4).strip()

        if victim.lower() == "victim":
            continue

        if set(victim) <= {"-", ":"}:
            continue

        if is_probable_victim(victim):

            victims.append({
                "victim": clean_victim_name(victim),
                "date": date,
                "source": source,
                "details": details,
            })

    return victims


def main():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    markdown_files = find_markdown_files()

    print(
        f"Found {len(markdown_files)} Markdown files."
    )

    all_victims = []

    for markdown_file in markdown_files:

        group = get_group_name(markdown_file)

        candidates = extract_victims_from_markdown(
            markdown_file
        )

        for candidate in candidates:

            candidate["group"] = group

            candidate["file"] = str(
                markdown_file.relative_to(ROOT_DIR)
            )

            all_victims.append(candidate)

    unique_victims = {}

    for victim in all_victims:

        normalized = normalize_name(
            victim["victim"]
        )

        key = (
            victim["group"].lower(),
            normalized
        )

        if key not in unique_victims:

            unique_victims[key] = victim

    unique_victims = list(
        unique_victims.values()
    )

    group_counts = defaultdict(int)

    for victim in unique_victims:

        group_counts[
            victim["group"]
        ] += 1

    statistics = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "groups": len(group_counts),

        "unique_victim_records": len(
            unique_victims
        ),

        "victims_by_group": dict(
            sorted(
                group_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
        )
    }

    victims_output = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "victims": unique_victims
    }

    VICTIMS_FILE.write_text(
        json.dumps(
            victims_output,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    VICTIM_COUNTS_FILE.write_text(
        json.dumps(
            statistics,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print()
    print("=" * 60)
    print("RANSOMWARE VICTIM TRACKER")
    print("=" * 60)

    print(
        f"Groups found: {statistics['groups']}"
    )

    print(
        f"Unique victim records: "
        f"{statistics['unique_victim_records']}"
    )

    print()
    print("Victims by group:")

    for group, count in (
        statistics["victims_by_group"].items()
    ):

        print(
            f"  {group}: {count}"
        )

    print()
    print(
        f"Created: {VICTIMS_FILE}"
    )

    print(
        f"Created: {VICTIM_COUNTS_FILE}"
    )


if __name__ == "__main__":
    main()
