import pytest
from beet import Context, DataPack
from beet.contrib.worldgen import WorldgenCarver, WorldgenConfiguredCarver

from beet_datapack_utils import CARVER, Target, targets, worldgen_config

FINAL_DENSITY = "minecraft:overworld/final_density"


def disable_canyons(ctx: Context):
    for target in targets(ctx):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0


# -- targets(ctx), run inside a beet build -------------------------------------


def test_targets(build):
    ctx = build()
    base, overlay = targets(ctx)
    assert (base.pack, base.version) == (ctx.data, "1.21.9")
    assert (overlay.pack, overlay.version) == (ctx.data.overlays["v26_3"], "26.3")


def test_missing_base_version(build):
    ctx = build(meta={"overlay_versions": {}})
    with pytest.raises(KeyError, match="base_version"):
        targets(ctx)


def test_patch_writes_each_version_in_its_format(build):
    ctx = build(disable_canyons)

    base = ctx.data[WorldgenConfiguredCarver]["minecraft:canyon"].data
    overlay = ctx.data.overlays["v26_3"][WorldgenCarver]["minecraft:canyon"].data
    assert base == {"type": "minecraft:canyon", "config": {"probability": 0}}
    assert overlay == {"type": "minecraft:canyon", "probability": 0}
    # The overlay only contains the new folder, the base only the old one.
    assert "minecraft:canyon" not in ctx.data.overlays["v26_3"][WorldgenConfiguredCarver]
    assert "minecraft:canyon" not in ctx.data[WorldgenCarver]


def test_vanilla_is_only_loaded_when_needed(build, fake_vanilla):
    build(lambda ctx: targets(ctx))
    assert fake_vanilla.instances == 0
    build(disable_canyons)
    assert fake_vanilla.instances == 1


# -- Target on its own ---------------------------------------------------------


def test_patch_accepts_plain_file_types(load_vanilla):
    target = Target(DataPack(), "1.21.9", load_vanilla)
    with target.patch(WorldgenConfiguredCarver, "minecraft:canyon") as carver:
        carver["config"]["probability"] = 0.5
    assert target.pack[WorldgenConfiguredCarver]["minecraft:canyon"].data["config"] == {
        "probability": 0.5
    }


def test_failed_patch_writes_nothing(load_vanilla):
    target = Target(DataPack(), "1.21.9", load_vanilla)
    with (
        pytest.raises(RuntimeError, match="boom"),
        target.patch(CARVER, "minecraft:canyon") as carver,
    ):
        worldgen_config(carver)["probability"] = 0
        raise RuntimeError("boom")
    assert "minecraft:canyon" not in target.pack[WorldgenConfiguredCarver]


def test_missing_file_has_helpful_error(load_vanilla):
    target = Target(DataPack(), "1.21.9", load_vanilla)
    with (
        pytest.raises(KeyError, match="minecraft:missing"),
        target.patch(CARVER, "minecraft:missing"),
    ):
        pass


def test_inline_density_function(load_vanilla):
    target = Target(DataPack(), "26.3", load_vanilla)
    inlined = target.inline_density_function(FINAL_DENSITY)
    assert inlined["type"] == "minecraft:min"
    inlined["left"] = 1  # a copy, vanilla stays untouched
    assert target.inline_density_function(FINAL_DENSITY)["left"] == "minecraft:a"
    assert target.inline_density_function({"type": "minecraft:add"}) == {"type": "minecraft:add"}


def test_vanilla_is_loaded_once_per_target(load_vanilla):
    loaded = []

    def counting_loader(version: str) -> DataPack:
        loaded.append(version)
        return load_vanilla(version)

    target = Target(DataPack(), "26.3", counting_loader)
    assert loaded == []
    target.inline_density_function(FINAL_DENSITY)
    target.inline_density_function(FINAL_DENSITY)
    assert loaded == ["26.3"]
