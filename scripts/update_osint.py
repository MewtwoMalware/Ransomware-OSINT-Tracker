import json
from pathlib import Path

INCIDENTS_FILE = Path("data/incidents.json")


def load_incidents():
    with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("Ransomware OSINT Tracker")
    print("========================")

    incidents = load_incidents()

    print(f"Current incidents: {len(incidents)}")
    print("OSINT updater completed successfully.")


if __name__ == "__main__":
    main()
