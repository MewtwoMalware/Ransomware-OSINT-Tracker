import json
from pathlib import Path

DATA = Path("data")


def check_file(filename):
    file = DATA / filename

    print(f"Checking {filename}...")

    try:
        with open(file, "r", encoding="utf-8") as f:
            json.load(f)

        print("✓ OK")

    except Exception as error:
        print("✗ ERROR")
        print(error)


print("Ransomware OSINT Tracker")
print("========================")

check_file("groups.json")
check_file("incidents.json")

print()
print("Finished.")
