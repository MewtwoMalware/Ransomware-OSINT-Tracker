import json
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


# Find the repository root
BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = BASE_DIR / "data" / "data" / "sources.json"
MARKDOWN_DIR = BASE_DIR


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


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


def read_feed(feed_url):
    request = Request(
        feed_url,
        headers={"User-Agent": "Ransomware-OSINT-Tracker/1.0"}
    )

    with urlopen(request, timeout=30) as response:
        return response.read()


def extract_items(feed_data):
    root = ET.fromstring(feed_data)
    items = []

    for item in root.findall(".//item"):
        title = item.findtext("title", default="").strip()
        link = item.findtext("link", default="").strip()
        description = item.findtext("description", default="").strip()
        guid = item.findtext("guid", default="").strip()
        pub_date = item.findtext("pubDate", default="").strip()

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "guid": guid,
            "pubDate": pub_date,
        })

    return items


def main():
    print("Ransomware OSINT Tracker")
    print("========================")
    print(f"Reading sources: {SOURCES_FILE}")

    sources = load_json(SOURCES_FILE)
    markdown_urls = get_markdown_urls()

    monitored_sources = [
        source
        for source in sources
        if source.get("monitor") is True and source.get("feed")
    ]

    print(f"Monitored RSS sources: {len(monitored_sources)}")
    print(f"Existing Markdown URLs: {len(markdown_urls)}")
    print()

    for source in monitored_sources:
        feed_url = source["feed"]
        domain = source.get("domain", "")

        print(f"Checking: {domain}")
        print(f"Feed: {feed_url}")

        try:
            feed_data = read_feed(feed_url)
            items = extract_items(feed_data)

            new_items = [
                item
                for item in items
                if item["link"] and item["link"] not in markdown_urls
            ]

            print(f"Feed items: {len(items)}")
            print(f"New article candidates: {len(new_items)}")

            for item in new_items:
                print(f"  - {item['title']}")
                print(f"    {item['link']}")
                print(f"    Published: {item['pubDate']}")

        except Exception as error:
            print(f"ERROR: Could not read feed: {error}")

        print()

    print("RSS monitoring completed.")
    print("NO FILES WERE MODIFIED.")


if __name__ == "__main__":
    main()
