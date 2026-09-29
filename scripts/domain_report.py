from collections import Counter
from pathlib import Path
from urllib.parse import urlparse
import re

BASE_DIR = Path(__file__).resolve().parent.parent

URL_PATTERN = re.compile(r"https?://[^\s)\]}>\"']+")

domains = Counter()

for file in BASE_DIR.rglob("*.md"):
    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for url in URL_PATTERN.findall(text):
        url = url.rstrip(".,;:")
        domain = urlparse(url).netloc.lower()
        if domain:
            domains[domain] += 1

print("OSINT Source Domain Report")
print("==========================")
print(f"Unique domains: {len(domains)}")
print()

for domain, count in domains.most_common():
    print(f"{count:4}  {domain}")
