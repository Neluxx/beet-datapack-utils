import pytest
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenConfiguredFeature,
    WorldgenFeature,
    WorldgenNoise,
)

from datapack_utils import CARVER, FEATURE, VersionedRegistry, resolve_registry


@pytest.mark.parametrize(
    ("version", "carver", "feature"),
    [
        ("1.19", WorldgenConfiguredCarver, WorldgenConfiguredFeature),
        ("26.2", WorldgenConfiguredCarver, WorldgenConfiguredFeature),
        ("26.3", WorldgenCarver, WorldgenFeature),
        ("27.1", WorldgenCarver, WorldgenFeature),
    ],
)
def test_builtin_registries(version, carver, feature):
    assert CARVER.resolve(version) is carver
    assert FEATURE.resolve(version) is feature


def test_plain_file_type_passes_through():
    assert resolve_registry(WorldgenNoise, "1.19") is WorldgenNoise


def test_changes_are_applied_in_version_order():
    registry = VersionedRegistry(
        WorldgenNoise, (("26.3", WorldgenFeature), ("1.21", WorldgenCarver))
    )
    assert registry.resolve("1.20") is WorldgenNoise
    assert registry.resolve("1.21.9") is WorldgenCarver
    assert registry.resolve("26.3") is WorldgenFeature
