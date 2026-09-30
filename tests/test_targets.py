import pytest
from beet import Context
from beet.contrib.worldgen import WorldgenCarver, WorldgenConfiguredCarver

from datapack_utils import CARVER, Target, Targets, Version, worldgen_config


def disable_canyons(ctx: Context):
    for target in ctx.inject(Targets):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0


def failing_patch(ctx: Context):
    for target in ctx.inject(Targets):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
            raise RuntimeError("boom")


def reuse_targets(ctx: Context):
    for target in ctx.inject(Targets):
        target.vanilla  # noqa: B018 - mount again through the shared service


def test_patch_writes_each_version_in_its_format(build):
    ctx = build(disable_canyons)

    base = ctx.data[WorldgenConfiguredCarver]["minecraft:canyon"].data
    overlay = ctx.data.overlays["v26_3"][WorldgenCarver]["minecraft:canyon"].data
    assert base == {"type": "minecraft:canyon", "config": {"probability": 0}}
    assert overlay == {"type": "minecraft:canyon", "probability": 0}
    # The overlay only contains the new folder, the base only the old one.
    assert "minecraft:canyon" not in ctx.data.overlays["v26_3"][WorldgenConfiguredCarver]
    assert "minecraft:canyon" not in ctx.data[WorldgenCarver]


def test_targets_are_shared_and_vanilla_is_mounted_once(build, fake_vanilla):
    ctx = build(disable_canyons, reuse_targets)
    assert ctx.inject(Targets) is ctx.inject(Targets)
    assert sorted(fake_vanilla.mounts) == ["1.21.9", "26.3"]


def test_vanilla_is_only_created_when_needed(build, fake_vanilla):
    ctx = build()
    for target in ctx.inject(Targets):
        assert target.pack is not None
    assert fake_vanilla.instances == 0

    build(disable_canyons)
    assert fake_vanilla.instances == 1


def test_target_properties(build):
    ctx = build()
    base, overlay = ctx.inject(Targets)
    assert (base.version, base.directory, base.is_overlay) == (Version("1.21.9"), None, False)
    assert (overlay.version, overlay.directory, overlay.is_overlay) == ("26.3", "v26_3", True)
    assert overlay.at_least("26.3") and not base.at_least("26.3")


def test_failed_patch_writes_nothing(build):
    ctx = build()
    with pytest.raises(RuntimeError, match="boom"):
        failing_patch(ctx)
    assert "minecraft:canyon" not in ctx.data[WorldgenConfiguredCarver]


def test_missing_file_has_helpful_error(build):
    ctx = build()
    base = next(iter(ctx.inject(Targets)))
    with pytest.raises(KeyError, match="minecraft:missing"):
        base.copy(WorldgenConfiguredCarver, "minecraft:missing")


def test_inline_density_function(build):
    ctx = build()
    _, overlay = ctx.inject(Targets)
    inlined = overlay.inline_density_function("minecraft:overworld/final_density")
    assert inlined["type"] == "minecraft:min"
    inlined["left"] = 1  # a copy, vanilla stays untouched
    assert overlay.inline_density_function("minecraft:overworld/final_density")["left"] == (
        "minecraft:a"
    )
    assert overlay.inline_density_function({"type": "minecraft:add"}) == {"type": "minecraft:add"}


def test_missing_base_version(build):
    with pytest.raises(Exception, match="base_version"):
        ctx = build(meta={"overlay_versions": {}})
        list(ctx.inject(Targets))


def test_target_without_vanilla():
    target = Target(pack=None, version=Version("26.3"))
    with pytest.raises(RuntimeError):
        target.vanilla  # noqa: B018
