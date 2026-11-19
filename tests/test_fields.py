import pytest

from beet_datapack_utils import resolve_key, set_range, worldgen_config


def test_worldgen_config():
    wrapped = {"type": "minecraft:canyon", "config": {"probability": 0.01}}
    flat = {"type": "minecraft:canyon", "probability": 0.01}
    assert worldgen_config(wrapped) is wrapped["config"]
    assert worldgen_config(flat) is flat


def test_resolve_key():
    assert resolve_key({"base_octave": -9}, "base_octave", "firstOctave") == "base_octave"
    assert resolve_key({"firstOctave": -9}, "base_octave", "firstOctave") == "firstOctave"
    with pytest.raises(KeyError):
        resolve_key({}, "a", "b")


def test_set_range_float_and_int():
    config = {
        "floats": {"type": "minecraft:uniform", "min_inclusive": 0.7, "max_exclusive": 1.4},
        "ints": {"type": "minecraft:uniform", "min_inclusive": 2, "max_inclusive": 5},
    }
    set_range(config, "floats", 0.8, 1.5)
    set_range(config, "ints", 0, 0)
    assert config == {
        "floats": {"type": "minecraft:uniform", "min_inclusive": 0.8, "max_exclusive": 1.5},
        "ints": {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 0},
    }


def test_set_range_before_1_20_5():
    config = {
        "radius": {"type": "minecraft:uniform", "value": {"min_inclusive": 2, "max_inclusive": 3}}
    }
    set_range(config, "radius", 2, 5)
    assert config["radius"]["value"] == {"min_inclusive": 2, "max_inclusive": 5}


@pytest.mark.parametrize("node", [3, {"type": "minecraft:constant", "value": 1}])
def test_set_range_rejects_non_ranges(node):
    with pytest.raises(ValueError, match="radius"):
        set_range({"radius": node}, "radius", 0, 1)
