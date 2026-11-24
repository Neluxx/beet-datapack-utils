import pytest
from beet import Context, DataPack
from beet.contrib.worldgen import WorldgenCarver, WorldgenConfiguredCarver, WorldgenDensityFunction

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


def test_unconfigured_overlay(build):
    ctx = build(meta={"base_version": "1.21.9", "overlay_versions": {"v26_3_typo": "26.3"}})
    with pytest.raises(KeyError, match="v26_3_typo"):
        targets(ctx)
    assert "v26_3_typo" not in set(ctx.data.overlays)


def test_unquoted_version(build):
    ctx = build(meta={"base_version": 1.2})
    with pytest.raises(TypeError, match="must be quoted"):
        targets(ctx)


def test_vanilla_is_the_exact_release(build, fake_vanilla):
    build(disable_canyons)
    assert sorted(fake_vanilla.loaded) == ["1.21.9", "26.3"]


def test_unknown_vanilla_release(build):
    with pytest.raises(KeyError, match="Minecraft 26 not found"):
        build(disable_canyons, meta={"base_version": "26"})


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


def test_second_patch_keeps_first_changes(load_vanilla):
    target = Target(DataPack(), "1.21.9", load_vanilla)
    with target.patch(CARVER, "minecraft:canyon") as carver:
        worldgen_config(carver)["probability"] = 0
    with target.patch(CARVER, "minecraft:canyon") as carver:
        worldgen_config(carver)["y"] = 5
    assert target.pack[WorldgenConfiguredCarver]["minecraft:canyon"].data["config"] == {
        "probability": 0,
        "y": 5,
    }


def test_failed_patch_keeps_existing_file(load_vanilla):
    target = Target(DataPack(), "1.21.9", load_vanilla)
    with target.patch(CARVER, "minecraft:canyon") as carver:
        worldgen_config(carver)["probability"] = 0
    with pytest.raises(RuntimeError), target.patch(CARVER, "minecraft:canyon") as carver:
        worldgen_config(carver)["probability"] = 1
        raise RuntimeError
    assert target.pack[WorldgenConfiguredCarver]["minecraft:canyon"].data["config"] == {
        "probability": 0
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


def test_failed_vanilla_load_is_not_reported_as_missing_file():
    def unknown_release(version: str) -> DataPack:
        raise KeyError(f"unknown release {version}")

    target = Target(DataPack(), "1.21.99", unknown_release)
    with (
        pytest.raises(KeyError, match=r"unknown release 1\.21\.99"),
        target.patch(CARVER, "minecraft:canyon"),
    ):
        pass


def test_vanilla_is_loaded_once_per_target(load_vanilla):
    loaded = []

    def counting_loader(version: str) -> DataPack:
        loaded.append(version)
        return load_vanilla(version)

    target = Target(DataPack(), "26.3", counting_loader)
    assert loaded == []
    with target.patch(CARVER, "minecraft:canyon"):
        pass
    with target.patch(WorldgenDensityFunction, FINAL_DENSITY):
        pass
    assert loaded == ["26.3"]
