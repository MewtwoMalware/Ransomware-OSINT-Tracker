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


def test_organization_must_be_dictionary():
    try:
        victim_tracker.validate_organization("invalid")
        assert False, "Expected ValueError for non-dictionary organization"

    except ValueError as error:
        assert str(error) == (
            "Organization entry must be a JSON object."
        )

def test_missing_required_organization_field():
    organization = {
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for missing organization_id"

    except ValueError as error:
        assert str(error) == (
            "Organization is missing required field: organization_id"
        )

def test_invalid_organization_id_format():
    organization = {
        "organization_id": "ORG-123",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid organization ID"

    except ValueError as error:
        assert str(error) == "Invalid organization ID format."

def test_empty_canonical_name():
    organization = {
        "organization_id": "ORG-000001",
        "canonical_name": "",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for empty canonical name"

    except ValueError as error:
        assert str(error) == "Canonical name must be a non-empty string."

def test_canonical_name_cannot_contain_only_spaces():
    organization = {
        "organization_id": "ORG-000002",
        "canonical_name": "   ",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for whitespace-only canonical name"

    except ValueError as error:
        assert str(error) == "Canonical name must be a non-empty string."

def test_aliases_must_be_a_list():
    organization = {
        "organization_id": "ORG-000003",
        "canonical_name": "Example Organization",
        "aliases": "Example",
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid aliases"

    except ValueError as error:
        assert str(error) == "Organization aliases must be a list."


def test_alias_cannot_be_empty():
    organization = {
        "organization_id": "ORG-000004",
        "canonical_name": "Example Organization",
        "aliases": [""],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for empty alias"

    except ValueError as error:
        assert str(error) == "Every alias must be a non-empty string."


def test_invalid_identity_status():
    organization = {
        "organization_id": "ORG-000005",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unknown",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid identity status"

    except ValueError as error:
        assert str(error) == "Invalid organization identity status."


def test_invalid_country_type():
    organization = {
        "organization_id": "ORG-000006",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "country": 123,
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid country"

    except ValueError as error:
        assert str(error) == "Organization country must be a string or null."


def test_invalid_sector_type():
    organization = {
        "organization_id": "ORG-000007",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "sector": 123,
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid sector"

    except ValueError as error:
        assert str(error) == "Organization sector must be a string or null."


def test_evidence_must_be_a_list():
    organization = {
        "organization_id": "ORG-000008",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": "invalid",
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid evidence"

    except ValueError as error:
        assert str(error) == "Organization evidence must be a list."


def test_verified_organization_requires_evidence():
    organization = {
        "organization_id": "ORG-000009",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "verified",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for missing evidence"

    except ValueError as error:
        assert str(error) == (
            "Verified organizations must have supporting evidence."
        )


def test_invalid_evidence_entry():
    organization = {
        "organization_id": "ORG-000010",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": ["invalid"],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid evidence entry"

    except ValueError as error:
        assert str(error) == "Evidence entries must be JSON objects."


def test_invalid_evidence_url():
    organization = {
        "organization_id": "ORG-000011",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [{
            "source_name": "Example Source",
            "source_url": "invalid-url",
            "description": "Example description",
            "checked_at": "2026-11-02T12:00:00"
        }],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid evidence URL"

    except ValueError as error:
        assert str(error) == (
            "Evidence source URL must use HTTP or HTTPS."
        )


def test_invalid_evidence_timestamp():
    organization = {
        "organization_id": "ORG-000012",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [{
            "source_name": "Example Source",
            "source_url": "https://example.com",
            "description": "Example description",
            "checked_at": "invalid-date"
        }],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid evidence timestamp"

    except ValueError as error:
        assert str(error) == (
            "Evidence checked_at must be a valid ISO timestamp."
        )


def test_invalid_created_at():
    organization = {
        "organization_id": "ORG-000013",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "invalid-date",
        "updated_at": "2026-11-02T12:00:00"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid created_at"

    except ValueError as error:
        assert str(error) == (
            "Organization created_at must be a valid ISO timestamp."
        )

def test_invalid_updated_at():
    organization = {
        "organization_id": "ORG-000014",
        "canonical_name": "Example Organization",
        "aliases": [],
        "identity_status": "unresolved",
        "evidence": [],
        "created_at": "2026-11-02T12:00:00",
        "updated_at": "invalid-date"
    }

    try:
        victim_tracker.validate_organization(organization)
        assert False, "Expected ValueError for invalid updated_at"

    except ValueError as error:
        assert str(error) == (
            "Organization updated_at must be a valid ISO timestamp."
        )


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

    test_organization_must_be_dictionary()
    print("PASS: Organization entry must be a dictionary.")
    
    test_missing_required_organization_field()
    print("PASS: Missing required organization field raises ValueError.")
    
    test_invalid_organization_id_format()
    print("PASS: Invalid organization ID format raises ValueError.")
        
    test_empty_canonical_name()
    print("PASS: Empty canonical name raises ValueError.")
        
    test_canonical_name_cannot_contain_only_spaces()
    print("PASS: Whitespace-only canonical name raises ValueError.")
        
    test_aliases_must_be_a_list()
    print("PASS: Aliases must be a list.")

    test_alias_cannot_be_empty()
    print("PASS: Empty aliases rejected.")

    test_invalid_identity_status()
    print("PASS: Invalid identity status rejected.")

    test_invalid_country_type()
    print("PASS: Invalid country type rejected.")

    test_invalid_sector_type()
    print("PASS: Invalid sector type rejected.")

    test_evidence_must_be_a_list()
    print("PASS: Evidence must be a list.")

    test_verified_organization_requires_evidence()
    print("PASS: Verified organizations require evidence.")

    test_invalid_evidence_entry()
    print("PASS: Invalid evidence entries rejected.")

    test_invalid_evidence_url()
    print("PASS: Invalid evidence URLs rejected.")

    test_invalid_evidence_timestamp()
    print("PASS: Invalid evidence timestamps rejected.")

    test_invalid_created_at()
    print("PASS: Invalid created_at rejected.")

    test_invalid_updated_at()
    print("PASS: Invalid updated_at rejected.")










