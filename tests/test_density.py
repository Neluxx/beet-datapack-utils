from datapack_utils import is_reference, unwrap


def test_density_references():
    cached_old = {"type": "minecraft:cache_once", "argument": "minecraft:overworld/sloped_cheese"}
    interpolated_new = {"type": "minecraft:interpolated", "input": cached_old}
    assert unwrap(interpolated_new) == "minecraft:overworld/sloped_cheese"
    assert is_reference("minecraft:overworld/sloped_cheese", "minecraft:overworld/sloped_cheese")
    assert is_reference(interpolated_new, "minecraft:overworld/sloped_cheese")
    assert not is_reference({"type": "minecraft:add", "left": 1}, "minecraft:a")
