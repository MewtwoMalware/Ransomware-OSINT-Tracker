import json
import re
from pathlib import Path
from urllib.parse import urlparse

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

SOURCES_FILE = BASE_DIR / "data" / "data" / "sources.json"

URL_PATTERN = re.compile(r"https?://[^\s)\]}>\"']+")

# Markdown table rows:
# | [Article title](URL) | Date | Details |
TABLE_ROW_PATTERN = re.compile(
    r"^\|\s*\[([^\]]+)\]\((https?://[^)]+)\)\s*\|\s*([^|]+)\s*\|\s*(.*?)\s*\|$"
)


def load_sources():
    """Load the existing source registry."""
    if not SOURCES_FILE.exists():
        return []

    with open(SOURCES_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def find_markdown_files():
    """Find ransomware Markdown files."""
    files = []

    for file in BASE_DIR.glob("*.md"):
        if file.name.lower() not in {
            "readme.md",
            "contributing.md",
            "license.md",
        }:
            files.append(file)

    return sorted(files)


def parse_markdown_file(file):
    """
    Extract ransomware name and source URLs
    from one Markdown ransomware file.
    """

    ransomware_name = file.stem

    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ransomware_name, []

    entries = []

    for line in text.splitlines():
        match = TABLE_ROW_PATTERN.match(line.strip())

        if not match:
            continue

        title = match.group(1).strip()
        url = match.group(2).strip()
        date = match.group(3).strip()
        details = match.group(4).strip()

        entries.append({
            "ransomware": ransomware_name,
            "title": title,
            "url": url,
            "date": date,
            "details": details,
        })

    return ransomware_name, entries


def main():
    print("Ransomware OSINT Candidate Detector")
    print("===================================")
    print()

    sources = load_sources()

    print(f"Source registry URLs: {len(sources)}")

    # Create a lookup of URLs already known to the tracker.
    known_urls = {
        source.get("url", "").rstrip(".,;:")
        for source in sources
        if source.get("url")
    }

    print(f"Known unique URLs: {len(known_urls)}")
    print()

    markdown_files = find_markdown_files()

    print(f"Ransomware Markdown files: {len(markdown_files)}")
    print()

    all_entries = []
    ransomware_counts = {}

    for file in markdown_files:
        ransomware_name, entries = parse_markdown_file(file)

        ransomware_counts[ransomware_name] = len(entries)
        all_entries.extend(entries)

    print("Markdown source entries")
    print("-----------------------")

    for ransomware_name, count in sorted(
        ransomware_counts.items(),
        key=lambda item: item[0].lower()
    ):
        print(f"{count:4}  {ransomware_name}")

    print()
    print(f"Total Markdown source entries: {len(all_entries)}")

    # Check whether every Markdown URL exists in sources.json.
    markdown_urls = {
        entry["url"].rstrip(".,;:")
        for entry in all_entries
    }

    missing_from_registry = markdown_urls - known_urls

    print()
    print("Registry consistency")
    print("--------------------")
    print(f"Markdown URLs:       {len(markdown_urls)}")
    print(f"Registry URLs:       {len(known_urls)}")
    print(f"Missing from registry: {len(missing_from_registry)}")

    if missing_from_registry:
        print()
        print("URLs found in Markdown but missing from sources.json:")
        print("-----------------------------------------------------")

        for url in sorted(missing_from_registry):
            print(url)

    # Look for duplicate URLs across Markdown files.
    url_locations = {}

    for entry in all_entries:
        url = entry["url"].rstrip(".,;:")

        url_locations.setdefault(url, []).append(
            entry["ransomware"]
        )

    duplicates = {
        url: groups
        for url, groups in url_locations.items()
        if len(groups) > 1
    }

    print()
    print("Duplicate source URLs")
    print("---------------------")
    print(f"Duplicate URLs: {len(duplicates)}")

    if duplicates:
        for url, groups in sorted(duplicates.items()):
            print()
            print(url)
            print("Appears in:", ", ".join(sorted(set(groups))))

    print()
    print("Candidate detector completed.")
    print()
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
