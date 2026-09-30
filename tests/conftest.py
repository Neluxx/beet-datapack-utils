import pytest
from beet import DataPack, run_beet
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenDensityFunction,
    worldgen,
)

import datapack_utils.targets

CANYON_OLD = {"type": "minecraft:canyon", "config": {"probability": 0.01}}
CANYON_NEW = {"type": "minecraft:canyon", "probability": 0.01}
FINAL_DENSITY = {"type": "minecraft:min", "left": "minecraft:a", "right": "minecraft:b"}


def vanilla_pack(version: str) -> DataPack:
    pack = DataPack()
    worldgen(pack)
    if version == "26.3":
        pack[WorldgenCarver]["minecraft:canyon"] = WorldgenCarver(CANYON_NEW)
        pack[WorldgenDensityFunction]["minecraft:overworld/final_density"] = (
            WorldgenDensityFunction(FINAL_DENSITY)
        )
    else:
        pack[WorldgenConfiguredCarver]["minecraft:canyon"] = WorldgenConfiguredCarver(CANYON_OLD)
    return pack


class FakeVanilla:
    """Stands in for beet's Vanilla service without downloading the game."""

    mounts: list[str] = []
    instances = 0

    def __init__(self, ctx=None):
        FakeVanilla.instances += 1
        self.releases = self

    def __getitem__(self, version: str):
        return self._Release(version)

    class _Release:
        def __init__(self, version: str):
            self.version = version

        def mount(self, _prefix: str):
            FakeVanilla.mounts.append(self.version)

            class Mounted:
                data = vanilla_pack(self.version)

            return Mounted()


@pytest.fixture
def fake_vanilla(monkeypatch):
    FakeVanilla.mounts = []
    FakeVanilla.instances = 0
    monkeypatch.setattr(datapack_utils.targets, "Vanilla", FakeVanilla)
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
