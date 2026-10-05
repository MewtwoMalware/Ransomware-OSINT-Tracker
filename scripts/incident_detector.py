import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = BASE_DIR / "data" / "data" / "sources.json"


RANSOMWARE_TERMS = [
    "ransomware",
    "ransomware group",
    "ransomware attack",
    "ransomware incident",
    "ransomware deployment",
    "ransom demand",
    "encrypted files",
    "data extortion",
    "double extortion",
]


INCIDENT_TERMS = [
    "breach",
    "attack",
    "intrusion",
    "victim",
    "target",
    "compromised",
    "deployment",
    "extortion",
]


def load_monitored_sources():
    with open(SOURCES_FILE, "r", encoding="utf-8") as file:
        sources = json.load(file)

    return [
        source
        for source in sources
        if source.get("monitor") is True and source.get("feed")
    ]
def get_markdown_urls():
    urls = set()

    for markdown_file in MARKDOWN_DIR.glob("*.md"):
        with open(markdown_file, "r", encoding="utf-8") as file:
            for line in file:
                start = 0

                while True:
                    start = line.find("](", start)

                    if start == -1:
                        break

                    start += 2
                    end = line.find(")", start)

                    if end == -1:
                        break

                    url = line[start:end].strip()

                    if url.startswith("http://") or url.startswith("https://"):
                        urls.add(url)

                    start = end + 1

    return urls


def get_feed_items(feed_url):
    request = urllib.request.Request(
        feed_url,
        headers={
            "User-Agent": "Ransomware-OSINT-Tracker/1.0"
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read()

    root = ET.fromstring(data)

    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        description = item.findtext("description", default="").strip()

        items.append({
            "title": title,
            "link": link,
            "description": description,
        })

    return items


def looks_like_incident_candidate(item):
    text = " ".join(
        [
            item.get("title", ""),
            item.get("description", ""),
        ]
    ).lower()

    has_ransomware_term = any(
        term in text for term in RANSOMWARE_TERMS
    )

    has_incident_term = any(
        term in text for term in INCIDENT_TERMS
    )

    return has_ransomware_term and has_incident_term


def main():
    print("Ransomware Incident Detector")
    print("============================")
    
    markdown_urls = get_markdown_urls()
    print(f"Existing Markdown URLs: {len(markdown_urls)}")
    
    sources = load_monitored_sources()

    print(f"Monitored RSS sources: {len(sources)}")

    total_candidates = 0

    for source in sources:
        domain = source.get("domain", "")
        feed_url = source.get("feed")

        print()
        print(f"Checking: {domain}")
        print(f"Feed: {feed_url}")

        try:
            items = get_feed_items(feed_url)
        except Exception as error:
            print(f"Feed error: {error}")
            continue

        candidates = [
            item
            for item in items
            if item.get("link") not in markdown_urls
            and looks_like_incident_candidate(item)
        ]


        print(f"Feed items: {len(items)}")
        print(f"Possible incident candidates: {len(candidates)}")

        for item in candidates:
            total_candidates += 1

            print(f"  - {item['title']}")
            print(f"    {item['link']}")

    print()
    print(f"Total possible incident candidates: {total_candidates}")
    print()
    print("Incident detection completed.")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
