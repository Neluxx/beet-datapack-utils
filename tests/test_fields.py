import pytest

from beet_datapack_utils import first_existing_key, get_config, set_range


def test_get_config_before_26_3():
    canyon = {"type": "minecraft:canyon", "config": {"probability": 0.01}}
    assert get_config(canyon) is canyon["config"]


def test_get_config_since_26_3():
    canyon = {"type": "minecraft:canyon", "probability": 0.01}
    assert get_config(canyon) is canyon


def test_first_existing_key():
    assert first_existing_key({"base_octave": -9}, "base_octave", "firstOctave") == "base_octave"
    assert first_existing_key({"firstOctave": -9}, "base_octave", "firstOctave") == "firstOctave"


def test_first_existing_key_without_match():
    with pytest.raises(KeyError, match="base_octave"):
        first_existing_key({}, "base_octave", "firstOctave")


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


@pytest.mark.parametrize("value", [3, {"type": "minecraft:constant", "value": 1}])
def test_set_range_rejects_non_ranges(value):
    with pytest.raises(ValueError, match="radius"):
        set_range({"radius": value}, "radius", 0, 1)
