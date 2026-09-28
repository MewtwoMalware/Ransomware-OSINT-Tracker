import json
import re
from pathlib import Path
from urllib.parse import urlparse

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Where the source registry will be saved
SOURCES_FILE = BASE_DIR / "data" / "data" / "sources.json"

# Find URLs in Markdown files
URL_PATTERN = re.compile(r"https?://[^\s)\]}>\"']+")

sources = set()

for file in BASE_DIR.rglob("*.md"):
    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for url in URL_PATTERN.findall(text):
        url = url.rstrip(".,;:")
        sources.add(url)


source_list = []

for url in sorted(sources):
    parsed = urlparse(url)

    source_list.append({
        "url": url,
        "domain": parsed.netloc,
        "category": "unknown",
        "monitor": False
    })


SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(SOURCES_FILE, "w", encoding="utf-8") as file:
    json.dump(source_list, file, indent=2, ensure_ascii=False)

print("Ransomware OSINT Tracker")
print("========================")
print(f"Found {len(source_list)} unique source URLs.")
print(f"Saved source registry to: {SOURCES_FILE}")

