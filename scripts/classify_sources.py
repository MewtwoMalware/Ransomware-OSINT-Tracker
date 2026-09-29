import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCES_FILE = BASE_DIR / "data" / "data" / "sources.json"


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
    "eset.com": "security_vendor",

    # Security / research organizations
    "sans.org": "security_research",
    "nccgroup.com": "security_research",
    "sygnia.co": "security_research",
    "eset.com": "security_vendor",
    "moxfive.com": "security_research",
    "fox-it.com": "security_research",
    "blog.fox-it.com": "security_research",
    "securityarsenal.com": "security_research",
    "adaptivesecurity.com": "security_research",
    "kelacyber.com": "security_research",
    "silentpush.com": "threat_intelligence",
    "threatpaper.com": "threat_intelligence",
    "threatcluster.io": "threat_intelligence",
    "gambit.security": "security_research",
    "kudelskisecurity.com": "security_research",
    "s-rminform.com": "security_research",
    "activesoc.blackhillsinfosec.com": "security_research",
    "labs.cloudsecurityalliance.org": "security_research",
    "uvcyber.com": "security_research",

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
    "redpiranha.net.au": "security_research",
}


def classify_domain(domain):
    """
    Match both exact domains and subdomains.

    Example:
    www.bleepingcomputer.com
    becomes:
    bleepingcomputer.com
    """
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


# Load existing source registry
if not SOURCES_FILE.exists():
    raise FileNotFoundError(f"Could not find {SOURCES_FILE}")

with open(SOURCES_FILE, "r", encoding="utf-8") as file:
    sources = json.load(file)


category_counts = Counter()
unknown_domains = Counter()

print("OSINT Source Classification Report")
print("==================================")
print()

for source in sources:
    domain = source.get("domain", "")
    category = classify_domain(domain)

    category_counts[category] += 1

    if category == "unknown":
        unknown_domains[domain] += 1


print(f"Total URLs: {len(sources)}")
print(f"Categories: {len(category_counts)}")
print()

print("URLs by category")
print("-----------------")

for category, count in category_counts.most_common():
    print(f"{count:4}  {category}")


print()
print("Unknown domains")
print("----------------")

if unknown_domains:
    for domain, count in unknown_domains.most_common():
        print(f"{count:4}  {domain}")
else:
    print("None")
