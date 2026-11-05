#!/usr/bin/env python3

"""
Ransomware OSINT Tracker
Victim Database Processor

Processes manually/automatically submitted victim records.

The ransomware Markdown timeline files are NOT modified.
"""

from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import urllib.request
import urllib.error

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"

VICTIMS_FILE = DATA_DIR / "victims.json"
ALIASES_FILE = DATA_DIR / "victim_aliases.json"
ORGANIZATIONS_FILE = DATA_DIR / "organizations.json"
QUEUE_FILE = DATA_DIR / "victim_queue.json"
STATISTICS_FILE = DATA_DIR / "statistics.json"


# =========================================================
# HELPERS
# =========================================================

def is_approved(record):
    """
    Return True only when a record has been
    explicitly approved for ingestion.
    """

    return record.get("review_status") == "approved"

def is_pending_review(record):
    """
    Return True when a record has not yet been approved
    or rejected.
    """

    return record.get("review_status", "pending") == "pending"

def print_review_summary(pending):
    """
    Display how many records need manual review.
    """

    awaiting_review = sum(
        1 for record in pending
        if is_pending_review(record)
    )

    approved = sum(
        1 for record in pending
        if is_approved(record)
    )

    rejected = sum(
        1 for record in pending
        if record.get("review_status") == "rejected"
    )

    print()
    print("VICTIM QUEUE REVIEW SUMMARY")
    print("-" * 35)
    print(f"Awaiting review: {awaiting_review}")
    print(f"Approved, awaiting processing: {approved}")
    print(f"Rejected, awaiting cleanup: {rejected}")

def print_pending_records(pending):
    """
    List records awaiting manual review.
    Does not approve, reject, or modify records.
    """

    awaiting = [
        record for record in pending
        if is_pending_review(record)
    ]

    print()
    print("RECORDS AWAITING MANUAL REVIEW")
    print("-" * 35)

    if not awaiting:
        print("No records awaiting review.")
        return

    for index, record in enumerate(awaiting, start=1):
        group = record.get("group", "Unknown")
        victim = record.get("victim", "Unknown")
        source = record.get("source", "Not provided")

        print(f"{index}. {group} -> {victim}")
        print(f"   Source: {source}")

def timestamp():
    return datetime.now(
        timezone.utc
    ).isoformat()

# =========================================================
# RANSOMLOOK API
# =========================================================

RANSOMLOOK_API_URL = (
    "https://www.ransomlook.io/api/posts?days=7"
)

RANSOMLOOK_TIMEOUT = 15


def fetch_ransomlook_posts(
    url=RANSOMLOOK_API_URL,
    timeout=RANSOMLOOK_TIMEOUT
):
    """
    Fetch recent victim claims from the RansomLook API.

    Returns:
        list: Validated list of RansomLook posts.

    Raises:
        ValueError: Invalid JSON or unexpected response structure.
        TimeoutError: API connection timed out.
        RuntimeError: HTTP or connection errors.
    """

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Ransomware-OSINT-Tracker/1.0",
            "Accept": "application/json"
        }
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=timeout
        ) as response:

            response_data = response.read().decode("utf-8")

    except urllib.error.HTTPError as error:

        raise RuntimeError(
            f"RansomLook API returned HTTP {error.code}."
        ) from error

    except TimeoutError as error:

        raise TimeoutError(
            "Connection to RansomLook API timed out."
        ) from error

    except urllib.error.URLError as error:

        if isinstance(error.reason, TimeoutError):
            raise TimeoutError(
                "Connection to RansomLook API timed out."
            ) from error

        raise RuntimeError(
            f"Could not connect to RansomLook API: {error.reason}"
        ) from error

    except OSError as error:

        raise RuntimeError(
            f"RansomLook connection failed: {error}"
        ) from error

    try:

        data = json.loads(response_data)

    except json.JSONDecodeError as error:

        raise ValueError(
            "RansomLook API returned invalid JSON."
        ) from error

    if not isinstance(data, dict):

        raise ValueError(
            "Unexpected RansomLook API response structure."
        )

    posts = data.get("posts")

    if not isinstance(posts, list):

        raise ValueError(
            "RansomLook API response must contain a posts list."
        )

    for post in posts:

        if not isinstance(post, dict):

            raise ValueError(
                "RansomLook API contains an invalid post entry."
            )

    return posts
# =========================================================
# RANSOMLOOK VICTIM IMPORT
# =========================================================

def convert_ransomlook_post(post):
    """
    Convert a RansomLook post into a tracker victim record.

    Imported records remain unverified claims.
    """

    if not isinstance(post, dict):
        return None

    group = post.get("group_name")
    victim = post.get("post_title")

    if not isinstance(group, str) or not group.strip():
        return None

    if not isinstance(victim, str) or not victim.strip():
        return None

    group = group.strip()
    victim = victim.strip()

    discovered = post.get("discovered")

    if not isinstance(discovered, str) or not discovered.strip():
        discovered = timestamp()

        return {
        "id": create_id(group, victim),
        "group": group,
        "victim": victim,
        "normalized_name": normalize_name(victim),
        "date": discovered,
        "status": "claimed",
        "confidence": "unverified",
        "country": "Unknown",
        "sector": "Unknown",
        "source": "RansomLook",
        "source_title": "",
        "notes": "",
        "added_at": timestamp()
    }

def import_ransomlook_posts(posts, existing_victims, aliases=None):
    if aliases is None:
        aliases = {}

    existing_ids = {
        record.get("id")
        for record in existing_victims
        if isinstance(record, dict)
    }

    imported = []

    for post in posts:
        record = convert_ransomlook_post(post)

        if record is None:
            continue

        canonical_victim = apply_alias(
            record["victim"],
            aliases
        )

        record["victim"] = canonical_victim
        record["normalized_name"] = normalize_name(
            canonical_victim
        )
        record["id"] = create_id(
            record["group"],
            canonical_victim
        )

        if record["id"] in existing_ids:
            continue

        existing_ids.add(record["id"])
        imported.append(record)

    return imported

def normalize_name(name):
    """
    Normalize victim names for duplicate detection.
    """

    name = str(name).lower().strip()

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


def create_id(group, victim):
    """
    Create a stable ID for a group/victim combination.
    """

    raw = (
        normalize_name(group)
        + ":"
        + normalize_name(victim)
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()[:16]


# =========================================================
# JSON LOADING
# =========================================================

def load_json(path, default):

    if not path.exists():
        return default

    try:
        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception as error:
        raise RuntimeError(
            f"Could not read or parse {path}. "
            "Please fix the file before running the tracker again."
        ) from error


def save_json(path, data):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(

        json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        ),

        encoding="utf-8"
    )


# =========================================================
# LOAD DATABASES
# =========================================================

def load_victims():

    data = load_json(
        VICTIMS_FILE,
        {
            "last_updated": None,
            "victims": []
        }
    )

    return data.get(
        "victims",
        []
    )

def validate_organization(organization):

    if not isinstance(organization, dict):
        raise ValueError(
            "Organization entry must be a JSON object."
        )

    required_fields = [
        "organization_id",
        "canonical_name",
        "aliases",
        "identity_status",
        "evidence",
        "created_at",
        "updated_at"
    ]

    for field in required_fields:
        if field not in organization:
            raise ValueError(
                f"Organization is missing required field: {field}"
            )

    organization_id = organization["organization_id"]

    if not isinstance(organization_id, str) or not re.fullmatch(
        r"ORG-\d{6}", organization_id
    ):
        raise ValueError("Invalid organization ID format.")

    canonical_name = organization["canonical_name"]

    if not isinstance(canonical_name, str) or not canonical_name.strip():
        raise ValueError("Canonical name must be a non-empty string.")

    aliases = organization["aliases"]

    if not isinstance(aliases, list):
        raise ValueError("Organization aliases must be a list.")

    for alias in aliases:
        if not isinstance(alias, str) or not alias.strip():
            raise ValueError("Every alias must be a non-empty string.")

    identity_status = organization["identity_status"]

    allowed_statuses = {
        "verified",
        "under_review",
        "unresolved"
    }

    if (
        not isinstance(identity_status, str)
        or identity_status not in allowed_statuses
    ):
        raise ValueError("Invalid organization identity status.")

    for field in ("country", "sector"):
        value = organization.get(field)

        if value is not None and not isinstance(value, str):
            raise ValueError(
                f"Organization {field} must be a string or null."
            )


    evidence = organization["evidence"]

    if not isinstance(evidence, list):
        raise ValueError("Organization evidence must be a list.")

    if identity_status == "verified" and not evidence:
        raise ValueError(
            "Verified organizations must have supporting evidence."
        )

    evidence_fields = [
        "source_name",
        "source_url",
        "description",
        "checked_at"
    ]

    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("Evidence entries must be JSON objects.")

        for field in evidence_fields:
            if field not in item:
                raise ValueError(
                    f"Evidence is missing required field: {field}"
                )

            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError(
                    f"Evidence field {field} must be a non-empty string."
                )

        if not item["source_url"].startswith(("https://", "http://")):
            raise ValueError("Evidence source URL must use HTTP or HTTPS.")

        try:
            datetime.fromisoformat(item["checked_at"])
        except ValueError:
            raise ValueError("Evidence checked_at must be a valid ISO timestamp.")

    for field in ("created_at", "updated_at"):
        try:
            if not isinstance(organization[field], str):
                raise ValueError()

            datetime.fromisoformat(organization[field])

        except ValueError:
            raise ValueError(
                f"Organization {field} must be a valid ISO timestamp."
            )

    return True


def load_organizations():

    data = load_json(
        ORGANIZATIONS_FILE,
        {
            "last_updated": None,
            "organizations": []
        }
    )

    if not isinstance(data, dict):
        raise ValueError(
            "Organization registry must be a JSON object."
        )

    organizations = data.get("organizations")

    if not isinstance(organizations, list):
        raise ValueError(
            "Organization registry must contain "
            "an organizations list."
        )

    return organizations

def load_aliases():

    return load_json(
        ALIASES_FILE,
        {}
    )


def load_queue():

    data = load_json(
        QUEUE_FILE,
        {
            "pending": []
        }
    )

    return data.get(
        "pending",
        []
    )


# =========================================================
# APPLY ALIASES
# =========================================================

def apply_alias(name, aliases):

    normalized = normalize_name(name)

    for alias, canonical_name in aliases.items():

        if normalize_name(alias) == normalized:
            return canonical_name

    return name


# =========================================================
# PROCESS QUEUE
# =========================================================

def process_queue(victims, aliases):

    pending = load_queue()

    if not pending:
        print("No pending victim records.")
        return victims, 0, 0

    print(
        f"Records awaiting review: {len(pending)}"
    )

    existing_ids = {
        victim.get("id")
        for victim in victims
    }

    added = 0
    duplicates = 0
    remaining = []

    for record in pending:

        if not is_approved(record):
            remaining.append(record)
            continue

        group = str(
            record.get("group", "")
        ).strip()

        victim_name = str(
            record.get("victim", "")
        ).strip()

        if not group or not victim_name:
            print(
                "Approved record has missing group or victim; "
                "leaving it in the queue."
            )
            remaining.append(record)
            continue

        victim_name = apply_alias(
            victim_name,
            aliases
        )

        record_id = create_id(
            group,
            victim_name
        )

        if record_id in existing_ids:
            print(
                f"DUPLICATE: {group} -> {victim_name}"
            )
            duplicates += 1
            continue

        new_victim = {
            "id": record_id,
            "group": group,
            "victim": victim_name,
            "normalized_name": normalize_name(victim_name),
            "date": record.get("date"),
            "status": record.get("status", "unknown"),
            "confidence": record.get("confidence", "unknown"),
            "country": record.get("country", "Unknown"),
            "sector": record.get("sector", "Unknown"),
            "source": record.get("source", ""),
            "source_title": record.get("source_title", ""),
            "notes": record.get("notes", ""),
            "added_at": timestamp()
        }

        victims.append(new_victim)
        existing_ids.add(record_id)
        added += 1

        print(
            f"APPROVED AND ADDED: {group} -> {victim_name}"
        )

    save_json(
        QUEUE_FILE,
        {"pending": remaining}
    )

    return victims, added, duplicates


# =========================================================
# GENERATE STATISTICS
# =========================================================

def generate_statistics(victims):

    victims_by_group = {}
    victims_by_status = {}
    victims_by_country = {}
    victims_by_sector = {}

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

        victims_by_group[group] = (
            victims_by_group.get(
                group,
                0
            ) + 1
        )

        victims_by_status[status] = (
            victims_by_status.get(
                status,
                0
            ) + 1
        )

        victims_by_country[country] = (
            victims_by_country.get(
                country,
                0
            ) + 1
        )

        victims_by_sector[sector] = (
            victims_by_sector.get(
                sector,
                0
            ) + 1
        )

    return {

        "last_updated":
            timestamp(),

        "total_unique_victims":
            len(victims),

        "total_recorded_claims":
            len(victims),

        "total_groups":
            len(victims_by_group),

        "victims_by_group":
            dict(
                sorted(
                    victims_by_group.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_status":
            dict(
                sorted(
                    victims_by_status.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_country":
            dict(
                sorted(
                    victims_by_country.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            ),

        "victims_by_sector":
            dict(
                sorted(
                    victims_by_sector.items(),
                    key=lambda item:
                        item[1],
                    reverse=True
                )
            )
    }


# =========================================================
# SAVE DATABASE
# =========================================================

def save_victims(victims):

    save_json(

        VICTIMS_FILE,

        {
            "last_updated":
                timestamp(),

            "victims":
                victims
        }
    )

def save_organizations(organizations):

    save_json(
        ORGANIZATIONS_FILE,
        {
            "last_updated": timestamp(),
            "organizations": organizations
        }
    )


# =========================================================
# MAIN
# =========================================================

def main():

    print()
    print("=" * 60)
    print(
        "RANSOMWARE OSINT VICTIM TRACKER"
    )
    print("=" * 60)

    victims = load_victims()

    aliases = load_aliases()

    # Import recent RansomLook victim claims
    print()
    print("Checking RansomLook for new victim claims...")

    ransomlook_added = 0

    try:
        ransomlook_posts = fetch_ransomlook_posts()

        ransomlook_victims = import_ransomlook_posts(
            ransomlook_posts,
            victims,
            aliases
        )

        for record in ransomlook_victims:
            victims.append(record)
            ransomlook_added += 1

        print(
            f"RansomLook claims imported: {ransomlook_added}"
        )

    except (RuntimeError, ValueError, TimeoutError) as error:
        print(f"RansomLook import unavailable: {error}")

    pending = load_queue()

    print_review_summary(pending)
    print_pending_records(pending)

    print()
    print(
        f"Existing victims: "
        f"{len(victims)}"
    )

    (
        victims,
        added,
        duplicates
    ) = process_queue(
        victims,
        aliases
    )

    save_victims(
        victims
    )

    statistics = generate_statistics(
        victims
    )

    save_json(
        STATISTICS_FILE,
        statistics
    )

    print()
    print("=" * 60)
    print("RESULT")
    print("=" * 60)

    print(
    f"Manually approved and added: {added}"
    )

    print(
    f"RansomLook claims imported: {ransomlook_added}"
    )

    print(
        f"Duplicates ignored: "
        f"{duplicates}"
    )

    print(
        f"Total unique victims: "
        f"{statistics['total_unique_victims']}"
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
        "Victim tracker completed."
    )


if __name__ == "__main__":

    main()
