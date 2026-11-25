import pytest
from beet.contrib.worldgen import (
    ConfiguredFeatureTag,
    WorldgenCarver,
    WorldgenCarverTag,
    WorldgenConfiguredCarver,
    WorldgenConfiguredCarverTag,
    WorldgenConfiguredFeature,
    WorldgenFeature,
    WorldgenFeatureTag,
)

from beet_datapack_utils import CARVER, CARVER_TAG, FEATURE, FEATURE_TAG
from beet_datapack_utils.file_types import MovedFileType


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


@pytest.mark.parametrize(
    ("version", "carver_tag", "feature_tag"),
    [
        ("26.2", WorldgenConfiguredCarverTag, ConfiguredFeatureTag),
        ("26.3", WorldgenCarverTag, WorldgenFeatureTag),
    ],
)
def test_builtin_tag_file_types(version, carver_tag, feature_tag):
    assert CARVER_TAG.for_version(version) is carver_tag
    assert FEATURE_TAG.for_version(version) is feature_tag


def test_since_is_inclusive():
    moved = MovedFileType(WorldgenConfiguredFeature, WorldgenFeature, since="1.21")
    assert moved.for_version("1.20.5") is WorldgenConfiguredFeature
    assert moved.for_version("1.21") is WorldgenFeature


def test_invalid_version():
    with pytest.raises(ValueError, match="pre1"):
        CARVER.for_version("26.3-pre1")
