import sys
from pathlib import Path

# Make the repository root available for imports.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.victim_tracker import apply_alias, load_aliases


def test_alias_matching():
    aliases = load_aliases()

    test_names = [
        "ACME Corp.",
        "Acme Corporation",
        "ACME Inc.",
        "Acme Incorporated",
    ]

    expected = "Acme Corporation"

    for name in test_names:
        result = apply_alias(name, aliases)

        assert result == expected, (
            f"Alias test failed for {name!r}: "
            f"expected {expected!r}, got {result!r}"
        )

        print(f"PASS: {name} -> {result}")

    print("\nAll alias tests passed!")


if __name__ == "__main__":
    test_alias_matching()
