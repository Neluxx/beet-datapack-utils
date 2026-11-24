import pytest
from beet import Context, DataPack
from beet.contrib.worldgen import WorldgenCarver, WorldgenConfiguredCarver

from beet_datapack_utils import CARVER, VersionedPack, get_config, versioned_packs

CANYON = "minecraft:canyon"


def disable_canyons(ctx: Context):
    for pack in versioned_packs(ctx):
        with pack.edit(CARVER, CANYON) as canyon:
            get_config(canyon)["probability"] = 0


def old_canyon_config(pack: VersionedPack) -> dict:
    return pack.data_pack[WorldgenConfiguredCarver][CANYON].data["config"]


# -- versioned_packs(ctx), run inside a beet build ------------------------------


def test_versioned_packs(build):
    ctx = build()
    base, overlay = versioned_packs(ctx)
    assert (base.data_pack, base.minecraft_version) == (ctx.data, "1.21.9")
    assert (overlay.data_pack, overlay.minecraft_version) == (ctx.data.overlays["v26_3"], "26.3")


def test_missing_base_version(build):
    ctx = build(meta={"overlay_versions": {}})
    with pytest.raises(ValueError, match="base_version"):
        versioned_packs(ctx)


def test_empty_overlay_versions(build):
    # An `overlay_versions:` key without entries is read as None.
    ctx = build(meta={"base_version": "1.21.9", "overlay_versions": None})
    assert [pack.minecraft_version for pack in versioned_packs(ctx)] == ["1.21.9"]


def test_unconfigured_overlay(build):
    ctx = build(meta={"base_version": "1.21.9", "overlay_versions": {"v26_3_typo": "26.3"}})
    with pytest.raises(ValueError, match="v26_3_typo"):
        versioned_packs(ctx)
    assert "v26_3_typo" not in set(ctx.data.overlays)


def test_unquoted_version(build):
    ctx = build(meta={"base_version": 1.2})
    with pytest.raises(TypeError, match="must be quoted"):
        versioned_packs(ctx)


def test_edit_writes_each_version_in_its_format(build):
    ctx = build(disable_canyons)

    base = ctx.data[WorldgenConfiguredCarver][CANYON].data
    overlay = ctx.data.overlays["v26_3"][WorldgenCarver][CANYON].data
    assert base == {"type": "minecraft:canyon", "config": {"probability": 0}}
    assert overlay == {"type": "minecraft:canyon", "probability": 0}
    # The overlay only contains the new folder, the base only the old one.
    assert CANYON not in ctx.data.overlays["v26_3"][WorldgenConfiguredCarver]
    assert CANYON not in ctx.data[WorldgenCarver]


def test_loads_the_exact_vanilla_release(build, fake_vanilla):
    build(disable_canyons)
    assert sorted(fake_vanilla.loaded) == ["1.21.9", "26.3"]


def test_unknown_vanilla_release(build):
    with pytest.raises(KeyError, match="Minecraft 26 not found"):
        build(disable_canyons, meta={"base_version": "26"})


def test_loads_vanilla_only_when_needed(build, fake_vanilla):
    build(versioned_packs)
    assert fake_vanilla.instances == 0
    build(disable_canyons)
    assert fake_vanilla.instances == 1


# -- VersionedPack on its own ---------------------------------------------------


def test_edit_accepts_plain_file_types(load_vanilla):
    pack = VersionedPack(DataPack(), "1.21.9", load_vanilla)
    with pack.edit(WorldgenConfiguredCarver, CANYON) as canyon:
        canyon["config"]["probability"] = 0.5
    assert old_canyon_config(pack) == {"probability": 0.5}


def test_second_edit_keeps_first_changes(load_vanilla):
    pack = VersionedPack(DataPack(), "1.21.9", load_vanilla)
    with pack.edit(CARVER, CANYON) as canyon:
        get_config(canyon)["probability"] = 0
    with pack.edit(CARVER, CANYON) as canyon:
        get_config(canyon)["y"] = 5
    assert old_canyon_config(pack) == {"probability": 0, "y": 5}


def test_failed_edit_keeps_existing_file(load_vanilla):
    pack = VersionedPack(DataPack(), "1.21.9", load_vanilla)
    with pack.edit(CARVER, CANYON) as canyon:
        get_config(canyon)["probability"] = 0
    with pytest.raises(RuntimeError), pack.edit(CARVER, CANYON) as canyon:
        get_config(canyon)["probability"] = 1
        raise RuntimeError
    assert old_canyon_config(pack) == {"probability": 0}


def test_failed_edit_writes_nothing(load_vanilla):
    pack = VersionedPack(DataPack(), "1.21.9", load_vanilla)
    with pytest.raises(RuntimeError), pack.edit(CARVER, CANYON) as canyon:
        get_config(canyon)["probability"] = 0
        raise RuntimeError
    assert CANYON not in pack.data_pack[WorldgenConfiguredCarver]


def test_edit_missing_file(load_vanilla):
    pack = VersionedPack(DataPack(), "1.21.9", load_vanilla)
    with (
        pytest.raises(KeyError, match=r"minecraft:missing .* not found in 1\.21\.9"),
        pack.edit(CARVER, "minecraft:missing"),
    ):
        pass


def test_loads_vanilla_once_per_pack(load_vanilla):
    loaded = []

    def counting_loader(version: str) -> DataPack:
        loaded.append(version)
        return load_vanilla(version)

    pack = VersionedPack(DataPack(), "26.3", counting_loader)
    assert loaded == []
    with pack.edit(CARVER, CANYON):
        pass
    with pytest.raises(KeyError), pack.edit(CARVER, "minecraft:missing"):
        pass
    assert loaded == ["26.3"]
