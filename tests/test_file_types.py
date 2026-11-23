import pytest
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenConfiguredFeature,
    WorldgenFeature,
)

from beet_datapack_utils import CARVER, FEATURE
from beet_datapack_utils.file_types import Moved


@pytest.mark.parametrize(
    ("version", "carver", "feature"),
    [
        ("1.19", WorldgenConfiguredCarver, WorldgenConfiguredFeature),
        ("1.21.9", WorldgenConfiguredCarver, WorldgenConfiguredFeature),
        ("26.2", WorldgenConfiguredCarver, WorldgenConfiguredFeature),
        ("26.3", WorldgenCarver, WorldgenFeature),
        ("27.1", WorldgenCarver, WorldgenFeature),
    ],
)
def test_builtin_file_types(version, carver, feature):
    assert CARVER.for_version(version) is carver
    assert FEATURE.for_version(version) is feature


def test_custom_moved_file_type():
    moved = Moved(WorldgenConfiguredFeature, WorldgenFeature, since="1.21")
    assert moved.for_version("1.20.5") is WorldgenConfiguredFeature
    assert moved.for_version("1.21") is WorldgenFeature


def test_invalid_version():
    with pytest.raises(ValueError, match="pre1"):
        CARVER.for_version("26.3-pre1")
