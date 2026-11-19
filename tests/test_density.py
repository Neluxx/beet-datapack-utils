import pytest

from beet_datapack_utils import is_reference, replace_nodes

SLOPED_CHEESE = "minecraft:overworld/sloped_cheese"


def test_is_reference():
    cached_old = {"type": "minecraft:cache_once", "argument": SLOPED_CHEESE}
    interpolated_new = {"type": "minecraft:interpolated", "input": cached_old}
    assert is_reference(SLOPED_CHEESE, SLOPED_CHEESE)
    assert is_reference(interpolated_new, SLOPED_CHEESE)
    assert not is_reference({"type": "minecraft:add", "argument1": SLOPED_CHEESE}, SLOPED_CHEESE)
    assert not is_reference({"type": "minecraft:cache_once"}, SLOPED_CHEESE)


def test_replace_nodes():
    tree = {"left": {"type": "min", "right": "noodle"}, "items": ["noodle", 1]}
    replace_nodes(tree, lambda node: node == "noodle", 1, count=2)
    assert tree == {"left": {"type": "min", "right": 1}, "items": [1, 1]}


def test_wrong_count_leaves_tree_untouched():
    tree = {"a": "x", "b": "x"}
    with pytest.raises(ValueError, match="Expected 1 matching node"):
        replace_nodes(tree, lambda node: node == "x", "y", count=1)
    assert tree == {"a": "x", "b": "x"}


def test_does_not_descend_into_matches():
    tree = {"a": {"type": "choice", "input": {"type": "choice"}}}
    replace_nodes(
        tree, lambda node: isinstance(node, dict) and node.get("type") == "choice", "gone", count=1
    )
    assert tree == {"a": "gone"}
