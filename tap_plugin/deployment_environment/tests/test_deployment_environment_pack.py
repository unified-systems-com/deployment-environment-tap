"""The dimension pack, proved by importing it into a grid (req-deployment-environment-pack, -keying).

Assertions are made against what came back out of the grid (the `dimension` rows), not against
the JSON file: what ships is a claim about the grid.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

BUNDLE = Path(__file__).resolve().parents[1] / "grift" / "dimensions.grift.json"
FAMILY = "deployment.environment"
SEEDED_KEYS = (f"{FAMILY}.staging", f"{FAMILY}.production")

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded() -> dict[str, object]:
    from tap_grid.grift import grift_import
    from tap_grid.models import Dimension

    result = grift_import(json.loads(BUNDLE.read_text(encoding="utf-8")))
    assert result.success, result
    return {row.name: row for row in Dimension.objects.filter(name__startswith=FAMILY)}


def test_pack_seeds_the_family_and_two_environments(seeded) -> None:
    """req-deployment-environment-pack-1: exactly the family node and staging + production."""
    assert set(seeded) == {FAMILY, *SEEDED_KEYS}


def test_every_node_states_the_keying_rule(seeded) -> None:
    """req-deployment-environment-keying-1: one key per environment, valued `member` — said on every node,
    so a reader who lands on any one of them learns the scheme."""
    for name, row in seeded.items():
        assert "deployment.environment.<name>" in row.description, name
        assert "member" in row.description, name


def test_family_node_says_it_is_never_a_key(seeded) -> None:
    """req-deployment-environment-keying-2: the bare family name is a dictionary entry, not a key."""
    assert "never carry this bare name as a key" in seeded[FAMILY].description


def test_reimport_is_idempotent(seeded) -> None:
    """Seeding twice leaves one row per name (ids are fixed in the bundle)."""
    from tap_grid.grift import grift_import
    from tap_grid.models import Dimension

    assert grift_import(json.loads(BUNDLE.read_text(encoding="utf-8"))).success
    assert Dimension.objects.filter(name__startswith=FAMILY).count() == 3
