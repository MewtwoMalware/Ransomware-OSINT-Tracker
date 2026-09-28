import json
from pathlib import Path

INCIDENTS_FILE = Path("data/incidents.json")


def load_incidents():
    with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_incidents(incidents):
    with open(INCIDENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(incidents, file, indent=2, ensure_ascii=False)
        file.write("\n")


def main():
    print("Ransomware OSINT Tracker")
    print("========================")
    print("OSINT updater started.")

    incidents = load_incidents()

    print(f"Current incidents: {len(incidents)}")
    print("Updater completed successfully.")


if __name__ == "__main__":
    main()
