from types import SimpleNamespace
from typing import ClassVar

import pytest
from beet import DataPack, run_beet
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    worldgen,
)

import beet_datapack_utils.packs

CANYON_OLD = {"type": "minecraft:canyon", "config": {"probability": 0.01}}
CANYON_NEW = {"type": "minecraft:canyon", "probability": 0.01}


def vanilla_pack(version: str) -> DataPack:
    pack = DataPack()
    worldgen(pack)
    if version == "26.3":
        pack[WorldgenCarver]["minecraft:canyon"] = WorldgenCarver(CANYON_NEW)
    else:
        pack[WorldgenConfiguredCarver]["minecraft:canyon"] = WorldgenConfiguredCarver(CANYON_OLD)
    return pack


# Newest first, like Mojang's manifest. "26.3.1" comes before "26.3" and
# would be returned by beet's prefix lookup for "26.3".
MANIFEST = {"versions": [{"id": "26.3.1"}, {"id": "26.3"}, {"id": "1.21.9"}]}


class FakeRelease:
    def __init__(self, version: str):
        self.version = version

    def mount(self, _prefix: str) -> SimpleNamespace:
        FakeVanilla.loaded.append(self.version)
        return SimpleNamespace(data=vanilla_pack(self.version))


class FakeReleaseRegistry(dict):
    """Stands in for beet's ReleaseRegistry, which downloads release info."""

    def __init__(self, *, runtimes, cache, manifest):
        super().__init__({v["id"]: FakeRelease(v["id"]) for v in manifest.data["versions"]})


class FakeVanilla:
    """Stands in for beet's Vanilla service without downloading the game."""

    instances = 0
    loaded: ClassVar[list[str]] = []

    def __init__(self, _ctx):
        FakeVanilla.instances += 1
        self.releases = SimpleNamespace(
            manifest=SimpleNamespace(data=MANIFEST), runtimes=None, cache=None
        )


@pytest.fixture
def load_vanilla():
    """A vanilla loader for creating a `VersionedPack` directly."""
    return vanilla_pack


@pytest.fixture
def fake_vanilla(monkeypatch):
    FakeVanilla.instances = 0
    FakeVanilla.loaded = []
    monkeypatch.setattr(beet_datapack_utils.packs, "Vanilla", FakeVanilla)
    monkeypatch.setattr(beet_datapack_utils.packs, "ReleaseRegistry", FakeReleaseRegistry)
    return FakeVanilla


@pytest.fixture
def build(fake_vanilla, tmp_path):
    """Set up a beet project, run the given plugins on it and return the context."""

    def run(*plugins, meta=None, overlays=None):
        config = {
            "meta": meta or {"base_version": "1.21.9", "overlay_versions": {"v26_3": "26.3"}},
            "data_pack": {"overlays": overlays or [{"directory": "v26_3", "formats": 121}]},
        }
        with run_beet(config, directory=tmp_path) as ctx:
            for plugin in plugins:
                plugin(ctx)
            return ctx

    return run
