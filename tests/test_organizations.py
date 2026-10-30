import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import victim_tracker


def test_missing_registry_returns_empty_list():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_path = victim_tracker.ORGANIZATIONS_FILE

        try:
            victim_tracker.ORGANIZATIONS_FILE = (
                Path(temp_dir) / "organizations.json"
            )

            organizations = victim_tracker.load_organizations()

            assert organizations == []

        finally:
            victim_tracker.ORGANIZATIONS_FILE = original_path


def test_valid_registry_loads_successfully():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_path = victim_tracker.ORGANIZATIONS_FILE

        try:
            registry_path = Path(temp_dir) / "organizations.json"

            registry_path.write_text(
                '{"last_updated": null, "organizations": []}',
                encoding="utf-8"
            )

            victim_tracker.ORGANIZATIONS_FILE = registry_path

            organizations = victim_tracker.load_organizations()

            assert organizations == []

        finally:
            victim_tracker.ORGANIZATIONS_FILE = original_path


def test_invalid_top_level_structure_raises_error():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_path = victim_tracker.ORGANIZATIONS_FILE

        try:
            registry_path = Path(temp_dir) / "organizations.json"

            registry_path.write_text(
                '[]',
                encoding="utf-8"
            )

            victim_tracker.ORGANIZATIONS_FILE = registry_path

            try:
                victim_tracker.load_organizations()
                assert False, "Expected ValueError for invalid registry structure"

            except ValueError:
                pass

        finally:
            victim_tracker.ORGANIZATIONS_FILE = original_path


def test_invalid_organizations_field_raises_error():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_path = victim_tracker.ORGANIZATIONS_FILE

        try:
            registry_path = Path(temp_dir) / "organizations.json"

            registry_path.write_text(
                '{"last_updated": null, "organizations": "invalid"}',
                encoding="utf-8"
            )

            victim_tracker.ORGANIZATIONS_FILE = registry_path

            try:
                victim_tracker.load_organizations()
                assert False, "Expected ValueError for invalid organizations field"

            except ValueError:
                pass

        finally:
            victim_tracker.ORGANIZATIONS_FILE = original_path


def test_save_empty_registry():
    with tempfile.TemporaryDirectory() as temp_dir:
        original_path = victim_tracker.ORGANIZATIONS_FILE

        try:
            registry_path = Path(temp_dir) / "organizations.json"

            victim_tracker.ORGANIZATIONS_FILE = registry_path

            victim_tracker.save_organizations([])

            import json

            saved_data = json.loads(
                registry_path.read_text(encoding="utf-8")
            )

            assert saved_data["organizations"] == []
            assert saved_data["last_updated"] is not None

        finally:
            victim_tracker.ORGANIZATIONS_FILE = original_path


if __name__ == "__main__":
    test_missing_registry_returns_empty_list()
    print("PASS: Missing registry returns an empty list.")

    test_valid_registry_loads_successfully()
    print("PASS: Valid registry loads successfully.")

    test_invalid_top_level_structure_raises_error()
    print("PASS: Invalid top-level structure raises ValueError.")

    test_invalid_organizations_field_raises_error()
    print("PASS: Invalid organizations field raises ValueError.")

    test_save_empty_registry()
    print("PASS: Empty registry saves successfully.")


