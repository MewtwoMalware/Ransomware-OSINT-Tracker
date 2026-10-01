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


# Domain classification rules
DOMAIN_CATEGORIES = {
    # News / journalism
    "bleepingcomputer.com": "news",
    "infosecurity-magazine.com": "news",
    "techcrunch.com": "news",
    "reuters.com": "news",
    "thehackernews.com": "news",
    "therecord.media": "news",
    "wired.com": "news",
    "theguardian.com": "news",
    "theregister.com": "news",
    "techradar.com": "news",
    "krebsonsecurity.com": "news",
    "securityweek.com": "news",
    "computerweekly.com": "news",
    "securityaffairs.com": "news",
    "itpro.com": "news",
    "cyberscoop.com": "news",
    "bankinfosecurity.com": "news",
    "bankinfosecurity.net": "news",
    "ft.com": "news",
    "axios.com": "news",
    "time.com": "news",
    "abc.net.au": "news",
    "lemonde.fr": "news",
    "crn.com": "news",
    "lemagit.fr": "news",
    "ukdefencejournal.org.uk": "news",

    # Government / law enforcement
    "justice.gov": "government",
    "gov.uk": "government",
    "cisa.gov": "government",
    "fbi.gov": "law_enforcement",
    "nca.gov.uk": "law_enforcement",
    "nationalcrimeagency.gov.uk": "law_enforcement",
    "europol.europa.eu": "law_enforcement",
    "interpol.int": "law_enforcement",
    "ncsc.nl": "government",
    "politie.nl": "law_enforcement",
    "state.gov": "government",
    "hhs.gov": "government",
    "cert.ssi.gouv.fr": "government",
    "ccb.belgium.be": "government",
    "cyber.gov.au": "government",
    "thaicert.or.th": "government",
    "schleswig-holstein.de": "government",
    "home.treasury.gov": "government",
    "cyberscotland.com": "government",

    # Threat intelligence / security research
    "attack.mitre.org": "threat_intelligence",
    "unit42.paloaltonetworks.com": "threat_intelligence",
    "research.checkpoint.com": "threat_intelligence",
    "blog.checkpoint.com": "threat_intelligence",
    "checkpoint.com": "security_vendor",
    "halcyon.ai": "threat_intelligence",
    "group-ib.com": "threat_intelligence",
    "blackpointcyber.com": "threat_intelligence",
    "huntress.com": "threat_intelligence",
    "flashpoint.io": "threat_intelligence",
    "eset.com": "security_vendor",
    "welivesecurity.com": "threat_intelligence",
    "sophos.com": "security_vendor",
    "trendmicro.com": "security_vendor",
    "microsoft.com": "security_vendor",
    "crowdstrike.com": "security_vendor",
    "mandiant.com": "threat_intelligence",
    "paloaltonetworks.com": "security_vendor",
    "talosintelligence.com": "threat_intelligence",
    "barracuda.com": "security_vendor",
    "rapid7.com": "security_vendor",
    "trellix.com": "security_vendor",
    "darktrace.com": "security_vendor",
    "threatdown.com": "security_vendor",
    "bitdefender.com": "security_vendor",
    "cynet.com": "security_vendor",
    "cloudsek.com": "threat_intelligence",
    "cyfirma.com": "threat_intelligence",
    "cyble.com": "threat_intelligence",
    "trmlabs.com": "threat_intelligence",
    "picussecurity.com": "security_vendor",
    "zerofox.com": "threat_intelligence",
    "cybelangel.com": "threat_intelligence",
    "galaxywarden.com": "threat_intelligence",
    "elliptic.co": "threat_intelligence",
    "silentpush.com": "threat_intelligence",
    "threatpaper.com": "threat_intelligence",
    "threatcluster.io": "threat_intelligence",

    # Security vendors
    "broadcom.com": "security_vendor",
    "cloud.google.com": "security_vendor",
    "esentire.com": "security_vendor",

    # Security / research organizations
    "sans.org": "security_research",
    "nccgroup.com": "security_research",
    "sygnia.co": "security_research",
    "moxfive.com": "security_research",
    "fox-it.com": "security_research",
    "blog.fox-it.com": "security_research",
    "securityarsenal.com": "security_research",
    "adaptivesecurity.com": "security_research",
    "kelacyber.com": "security_research",
    "gambit.security": "security_research",
    "kudelskisecurity.com": "security_research",
    "s-rminform.com": "security_research",
    "activesoc.blackhillsinfosec.com": "security_research",
    "labs.cloudsecurityalliance.org": "security_research",
    "uvcyber.com": "security_research",
    "dcso.de": "security_research",
    "redpiranha.net.au": "security_research",

    # Ransomware / cybercrime-specific sources
    "nomoreransom.org": "ransomware",
    "ransomnews.com": "ransomware",
    "ransomwarewire.com": "ransomware",
    "darkwebsonar.io": "ransomware",
    "breached.company": "breach",
    "cyberbreaches.org": "breach",
    "invaders.ie": "cybercrime",
    "osintsearch.org": "osint",
    "malwaretips.com": "security_research",
    "securitytribune.com": "security_research",
    "ervik.as": "security_research",
}


def classify_domain(domain):
    """Return the category for a domain."""
    domain = domain.lower().strip()

    if domain.startswith("www."):
        domain = domain[4:]

    for known_domain, category in DOMAIN_CATEGORIES.items():
        known_domain = known_domain.lower()

        if known_domain.startswith("www."):
            known_domain = known_domain[4:]

        if domain == known_domain or domain.endswith("." + known_domain):
            return category

    return "unknown"


sources = set()

# Find URLs in Markdown files
for file in BASE_DIR.rglob("*.md"):
    try:
        text = file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue

    for url in URL_PATTERN.findall(text):
        url = url.rstrip(".,;:")
        sources.add(url)

# Preserve existing monitoring settings
existing_monitor_settings = {}

if SOURCES_FILE.exists():
    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as file:
            existing_sources = json.load(file)

        for source in existing_sources:
            existing_monitor_settings[source["url"]] = source.get("monitor", False)

    except (json.JSONDecodeError, KeyError, TypeError):
        existing_monitor_settings = {}

# Preserve existing feed settings
existing_feed_settings = {}

if SOURCES_FILE.exists():
    try:
        with open(SOURCES_FILE, "r", encoding="utf-8") as file:
            existing_sources = json.load(file)

        for source in existing_sources:
            if source.get("feed"):
                existing_feed_settings[source["url"]] = source["feed"]

    except (json.JSONDecodeError, KeyError, TypeError):
        existing_feed_settings = {}

source_list = []

for url in sorted(sources):
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    source_list.append({
    "url": url,
    "domain": domain,
    "category": classify_domain(domain),
    "monitor": existing_monitor_settings.get(url, False),
    "feed": existing_feed_settings.get(url)
})

SOURCES_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(SOURCES_FILE, "w", encoding="utf-8") as file:
    json.dump(source_list, file, indent=2, ensure_ascii=False)

print("Ransomware OSINT Tracker")
print("========================")
print(f"Found {len(source_list)} unique source URLs.")
print(f"Saved source registry to: {SOURCES_FILE}")

# Show category totals
from collections import Counter

category_counts = Counter(source["category"] for source in source_list)

print()
print("Categories:")
for category, count in category_counts.most_common():
    print(f"  {category}: {count}")
