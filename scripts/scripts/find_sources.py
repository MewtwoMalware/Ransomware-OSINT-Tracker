import re
from pathlib import Path

# Repository root
BASE_DIR = Path(__file__).resolve().parent.parent

# Find all Markdown files in the repository
markdown_files = BASE_DIR.rglob("*.md")

# Match normal http/https URLs
url_pattern = re.compile(r"https?://[^\s)\]}>\"']+")

sources = set()

for file in markdown_files:
    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for url in url_pattern.findall(text):
        # Remove common punctuation at the end of a URL
        url = url.rstrip(".,;:")

        sources.add(url)

print("Ransomware OSINT Tracker")
print("========================")
print(f"Found {len(sources)} unique source URLs.")
print()

for source in sorted(sources):
    print(source)
