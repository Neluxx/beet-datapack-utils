import pytest

from datapack_utils import find_nodes, replace_nodes


def test_find_nodes():
    tree = {"a": ["x", {"b": "x"}], "c": "y"}
    assert list(find_nodes(tree, lambda node: node == "x")) == ["x", "x"]


def test_replace_nodes():
    tree = {"left": {"type": "min", "right": "noodle"}, "items": ["noodle", 1]}
    assert replace_nodes(tree, lambda node: node == "noodle", 1) == 2
    assert tree == {"left": {"type": "min", "right": 1}, "items": [1, 1]}


def test_replace_nodes_expected_count_leaves_tree_untouched():
    tree = {"a": "x", "b": "x"}
    with pytest.raises(ValueError, match="Expected 1"):
        replace_nodes(tree, lambda node: node == "x", "y", expected=1)
    assert tree == {"a": "x", "b": "x"}
    assert replace_nodes(tree, lambda node: node == "x", "y", expected=2) == 2


def test_replace_nodes_does_not_descend_into_matches():
    tree = {"a": {"type": "choice", "input": {"type": "choice"}}}
    match = lambda node: isinstance(node, dict) and node.get("type") == "choice"  # noqa: E731
    assert replace_nodes(tree, match, "gone", expected=1) == 1
    assert tree == {"a": "gone"}
