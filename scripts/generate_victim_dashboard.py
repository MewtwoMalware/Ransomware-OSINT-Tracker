#!/usr/bin/env python3

from pathlib import Path
import json


ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

STATISTICS_FILE = DATA_DIR / "statistics.json"

DASHBOARD_FILE = ROOT_DIR / "victim-dashboard.md"


def load_statistics():

    if not STATISTICS_FILE.exists():

        return {
            "last_updated": None,
            "total_unique_victims": 0,
            "total_groups": 0,
            "victims_by_group": {},
            "victims_by_status": {},
            "victims_by_country": {},
            "victims_by_sector": {}
        }

    return json.loads(
        STATISTICS_FILE.read_text(
            encoding="utf-8"
        )
    )


def main():

    statistics = load_statistics()

    lines = []

    lines.append("# Ransomware Victim Tracker")
    lines.append("")

    lines.append(
        f"**Last updated:** "
        f"{statistics.get('last_updated', 'Unknown')}"
    )

    lines.append("")

    lines.append("## Overview")
    lines.append("")

    lines.append(
        f"- **Total unique victims:** "
        f"{statistics.get('total_unique_victims', 0)}"
    )

    lines.append(
        f"- **Groups represented:** "
        f"{statistics.get('total_groups', 0)}"
    )

    lines.append("")

    lines.append("## Victims by Ransomware Group")
    lines.append("")

    lines.append(
        "| Rank | Ransomware Group | Victims |"
    )

    lines.append(
        "| ---: | --- | ---: |"
    )

    groups = statistics.get(
        "victims_by_group",
        {}
    )

    for rank, (group, count) in enumerate(
        groups.items(),
        start=1
    ):

        lines.append(
            f"| {rank} | {group} | {count} |"
        )

    if not groups:

        lines.append(
            "| - | No victim records yet | 0 |"
        )

    lines.append("")

    lines.append("## Victims by Status")
    lines.append("")

    lines.append(
        "| Status | Victims |"
    )

    lines.append(
        "| --- | ---: |"
    )

    for status, count in (
        statistics.get(
            "victims_by_status",
            {}
        ).items()
    ):

        lines.append(
            f"| {status} | {count} |"
        )

    lines.append("")

    lines.append("## Victims by Country")
    lines.append("")

    lines.append(
        "| Country | Victims |"
    )

    lines.append(
        "| --- | ---: |"
    )

    for country, count in (
        statistics.get(
            "victims_by_country",
            {}
        ).items()
    ):

        lines.append(
            f"| {country} | {count} |"
        )

    lines.append("")

    lines.append("## Victims by Sector")
    lines.append("")

    lines.append(
        "| Sector | Victims |"
    )

    lines.append(
        "| --- | ---: |"
    )

    for sector, count in (
        statistics.get(
            "victims_by_sector",
            {}
        ).items()
    ):

        lines.append(
            f"| {sector} | {count} |"
        )

    lines.append("")

    lines.append(
        "---"
    )

    lines.append("")

    lines.append(
        "This dashboard is automatically generated "
        "from `data/statistics.json`."
    )

    DASHBOARD_FILE.write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8"
    )

    print(
        f"Dashboard generated: "
        f"{DASHBOARD_FILE}"
    )


if __name__ == "__main__":

    main()
