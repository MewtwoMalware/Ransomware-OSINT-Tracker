import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import victim_tracker


def test_missing_registry_returns_empty_list(): with tempfile.TemporaryDirectory() as temp_dir: original_path = victim_tracker.ORGANIZATIONS_FILE

    try:
        victim_tracker.ORGANIZATIONS_FILE = (
            Path(temp_dir) / "organizations.json"
        )

        organizations = victim_tracker.load_organizations()

        assert organizations == []

    finally:
        victim_tracker.ORGANIZATIONS_FILE = original_path


if name == "main": test_missing_registry_returns_empty_list() print("PASS: Missing registry returns an empty list.")
