#!/usr/bin/env python3

"""
Ransomware OSINT Tracker
Victim Database Generator

This program works alongside the existing ransomware
timeline Markdown files.

The Markdown files are NOT modified.

Victims are stored separately in:

data/victims.json
data/victim_aliases.json
data/statistics.json
"""

from pathlib import Path
from datetime import datetime, timezone
import json
import re


# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

VICTIMS_FILE = DATA_DIR / "victims.json"

ALIASES_FILE = DATA_DIR / "victim_aliases.json"

STATISTICS_FILE = DATA_DIR / "statistics.json"


# =========================================================
# DIRECTORY SETTINGS
# =========================================================

IGNORED_DIRECTORIES = {
    ".git",
    ".github",
    "scripts",
    "data",
    "node_modules",
}


# =========================================================
# BASIC HELPERS
# =========================================================

def normalize_name(name):
    """
    Creates a normalized version of a victim name.

    This helps prevent obvious duplicates such as:

    Acme Corp
    Acme Corporation
    ACME CORP.
    """

    name = name.lower().strip()

    name = re.sub(
        r"[^\w\s]",
        "",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

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

            name = name[
                :-len(suffix)
            ].strip()

    return name


def current_timestamp():
    """
    Returns the current UTC timestamp.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# FIND GROUP FILES
# =========================================================

def find_group_files():

    files = []

    for file in ROOT_DIR.rglob("*.md"):

        if any(
            directory in file.parts
            for directory in IGNORED_DIRECTORIES
        ):
            continue

        if file.name.lower() == "readme.md":
            continue

        files.append(file)

    return sorted(files)


# =========================================================
# IDENTIFY GROUP
# =========================================================

def get_group_name(file):

    try:

        content = file.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception:

        return file.stem

    match = re.search(
        r"^#\s+(.+?)\s*$",
        content,
        re.MULTILINE
    )

    if match:

        return match.group(1).strip()

    return file.stem


# =========================================================
# READ EXISTING VICTIM DATABASE
# =========================================================

def load_victims():

    if not VICTIMS_FILE.exists():

        return []

    try:

        data = json.loads(
            VICTIMS_FILE.read_text(
                encoding="utf-8"
            )
        )

        return data.get(
            "victims",
            []
        )

    except Exception:

        print(
            "Warning: Could not read victims.json"
        )

        return []


# =========================================================
# READ ALIASES
# =========================================================

def load_aliases():

    if not ALIASES_FILE.exists():

        return {}

    try:

        return json.loads(
            ALIASES_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        print(
            "Warning: Could not read victim_aliases.json"
        )

        return {}


# =========================================================
# SAVE VICTIMS
# =========================================================

def save_victims(victims):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output = {

        "last_updated":
            current_timestamp(),

        "victims":
            victims

    }

    VICTIMS_FILE.write_text(

        json.dumps(
            output,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"
    )


# =========================================================
# SAVE ALIASES
# =========================================================

def save_aliases(aliases):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ALIASES_FILE.write_text(

        json.dumps(
            aliases,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"
    )


# =========================================================
# GENERATE STATISTICS
# =========================================================

def generate_statistics(victims):

    group_counts = {}

    status_counts = {}

    country_counts = {}

    sector_counts = {}

    for victim in victims:

        group = victim.get(
            "group",
            "Unknown"
        )

        status = victim.get(
            "status",
            "unknown"
        )

        country = victim.get(
            "country",
            "Unknown"
        )

        sector = victim.get(
            "sector",
            "Unknown"
        )

        group_counts[group] = (
            group_counts.get(
                group,
                0
            ) + 1
        )

        status_counts[status] = (
            status_counts.get(
                status,
                0
            ) + 1
        )

        country_counts[country] = (
            country_counts.get(
                country,
                0
            ) + 1
        )

        sector_counts[sector] = (
            sector_counts.get(
                sector,
                0
            ) + 1
        )

    statistics = {

        "last_updated":
            current_timestamp(),

        "total_unique_victims":
            len(victims),

        "total_groups":
            len(group_counts),

        "victims_by_group":
            dict(
                sorted(
                    group_counts.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_status":
            dict(
                sorted(
                    status_counts.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_country":
            dict(
                sorted(
                    country_counts.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_sector":
            dict(
                sorted(
                    sector_counts.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            )
    }

    STATISTICS_FILE.write_text(

        json.dumps(
            statistics,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"
    )

    return statistics


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print(
        "=" * 60
    )

    print(
        "RANSOMWARE OSINT VICTIM TRACKER"
    )

    print(
        "=" * 60
    )

    group_files = find_group_files()

    print(
        f"\nMarkdown group files found: "
        f"{len(group_files)}"
    )

    for file in group_files:

        group = get_group_name(
            file
        )

        print(
            f"  - {group}"
        )

    victims = load_victims()

    aliases = load_aliases()

    print(
        f"\nExisting victim records: "
        f"{len(victims)}"
    )

    print(
        f"Existing aliases: "
        f"{len(aliases)}"
    )

    statistics = generate_statistics(
        victims
    )

    save_victims(
        victims
    )

    save_aliases(
        aliases
    )

    print()
    print(
        "=" * 60
    )

    print(
        "CURRENT STATISTICS"
    )

    print(
        "=" * 60
    )

    print(
        f"Total victims: "
        f"{statistics['total_unique_victims']}"
    )

    print(
        f"Groups represented: "
        f"{statistics['total_groups']}"
    )

    print()
    print(
        "Victims by group:"
    )

    for group, count in (
        statistics[
            "victims_by_group"
        ].items()
    ):

        print(
            f"  {group}: {count}"
        )

    print()
    print(
        "Tracker files generated:"
    )

    print(
        f"  {VICTIMS_FILE}"
    )

    print(
        f"  {ALIASES_FILE}"
    )

    print(
        f"  {STATISTICS_FILE}"
    )

    print()
    print(
        "Existing Markdown files were NOT modified."
    )


if __name__ == "__main__":

    main()
