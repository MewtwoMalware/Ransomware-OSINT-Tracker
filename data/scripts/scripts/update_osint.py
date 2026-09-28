import json
from pathlib import Path

# Find the repository root, regardless of where the script is run from
BASE_DIR = Path(__file__).resolve().parent.parent
INCIDENTS_FILE = BASE_DIR / "data" / "incidents.json"


def load_incidents():
    with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("Ransomware OSINT Tracker")
    print("========================")
    print(f"Reading: {INCIDENTS_FILE}")

    incidents = load_incidents()

    print(f"Current incidents: {len(incidents)}")
    print("OSINT updater completed successfully.")


if __name__ == "__main__":
    main()
