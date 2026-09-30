import pytest

from datapack_utils import octave_key, provider, resolve_key, set_range, worldgen_config


def test_worldgen_config():
    wrapped = {"type": "minecraft:canyon", "config": {"probability": 0.01}}
    flat = {"type": "minecraft:canyon", "probability": 0.01}
    assert worldgen_config(wrapped) is wrapped["config"]
    assert worldgen_config(flat) is flat


def test_resolve_key():
    assert resolve_key({"yScale": 1}, "room_vertical_radius_multiplier", "yScale") == "yScale"
    with pytest.raises(KeyError):
        resolve_key({}, "a", "b")


def test_octave_key():
    assert octave_key({"firstOctave": -9}) == "firstOctave"
    assert octave_key({"base_octave": -9, "base_amplitude": 0.9}) == "base_octave"


def test_provider_unwraps_legacy_value():
    legacy = {"radius": {"type": "minecraft:uniform", "value": {"min_inclusive": 2}}}
    modern = {"radius": {"type": "minecraft:uniform", "min_inclusive": 2}}
    assert provider(legacy, "radius") == {"min_inclusive": 2}
    assert provider(modern, "radius") is modern["radius"]
    with pytest.raises(TypeError):
        provider({"radius": 3}, "radius")


def test_set_range_float_and_int():
    floats = {"type": "minecraft:uniform", "min_inclusive": 0.7, "max_exclusive": 1.4}
    ints = {"type": "minecraft:uniform", "min_inclusive": 2, "max_inclusive": 5}
    set_range(floats, 0.8, 1.5)
    set_range(ints, 0, 0)
    assert floats == {"type": "minecraft:uniform", "min_inclusive": 0.8, "max_exclusive": 1.5}
    assert ints == {"type": "minecraft:uniform", "min_inclusive": 0, "max_inclusive": 0}
    with pytest.raises(KeyError):
        set_range({"type": "minecraft:constant", "value": 1}, 0, 1)
