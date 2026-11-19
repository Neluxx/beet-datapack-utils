import pytest
from beet import Context
from beet.contrib.worldgen import WorldgenCarver, WorldgenConfiguredCarver

from beet_datapack_utils import CARVER, targets, worldgen_config


def disable_canyons(ctx: Context):
    for target in targets(ctx):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0


def failing_patch(ctx: Context):
    for target in targets(ctx):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
            raise RuntimeError("boom")


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


def test_patch_accepts_plain_file_types(build):
    ctx = build()
    base, _ = targets(ctx)
    with base.patch(WorldgenConfiguredCarver, "minecraft:canyon") as carver:
        carver["config"]["probability"] = 0.5
    assert ctx.data[WorldgenConfiguredCarver]["minecraft:canyon"].data["config"] == {
        "probability": 0.5
    }


def test_vanilla_is_only_loaded_when_needed(build, fake_vanilla):
    build(lambda ctx: targets(ctx))
    assert fake_vanilla.instances == 0
    build(disable_canyons)
    assert fake_vanilla.instances == 1


def test_failed_patch_writes_nothing(build):
    ctx = build()
    with pytest.raises(RuntimeError, match="boom"):
        failing_patch(ctx)
    assert "minecraft:canyon" not in ctx.data[WorldgenConfiguredCarver]


def test_missing_file_has_helpful_error(build):
    ctx = build()
    base, _ = targets(ctx)
    with (
        pytest.raises(KeyError, match="minecraft:missing"),
        base.patch(CARVER, "minecraft:missing"),
    ):
        pass


def test_inline_density_function(build):
    ctx = build()
    _, overlay = targets(ctx)
    inlined = overlay.inline_density_function("minecraft:overworld/final_density")
    assert inlined["type"] == "minecraft:min"
    inlined["left"] = 1  # a copy, vanilla stays untouched
    again = overlay.inline_density_function("minecraft:overworld/final_density")
    assert again["left"] == "minecraft:a"
    assert overlay.inline_density_function({"type": "minecraft:add"}) == {"type": "minecraft:add"}
