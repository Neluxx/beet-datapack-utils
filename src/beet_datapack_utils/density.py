"""Find and replace nodes in density functions."""

from collections.abc import Callable, Iterator
from typing import Any

__all__ = ["is_reference", "replace_nodes"]

# Density function types that only wrap their input for caching/interpolation.
_WRAPPER_TYPES = frozenset(
    {
        "minecraft:cache_2d",
        "minecraft:cache_all_in_cell",
        "minecraft:cache_once",
        "minecraft:flat_cache",
        "minecraft:interpolated",
    }
)


def is_reference(node: Any, function_id: str) -> bool:
    """Return True if `node` references `function_id`, directly or through cache wrappers.

    The wrapped function is stored in `argument` before 26.3 and in `input` since 26.3.

    >>> is_reference({"type": "minecraft:cache_once", "argument": "minecraft:a"}, "minecraft:a")
    True
    """
    while isinstance(node, dict) and node.get("type") in _WRAPPER_TYPES:
        node = node.get("input", node.get("argument"))
    return node == function_id


def replace_nodes(tree: Any, match: Callable[[Any], bool], replacement: Any, *, count: int) -> None:
    """Replace every node below `tree` for which `match(node)` is True.

    Exactly `count` nodes must match. Otherwise a `ValueError` is raised and
    nothing changes, so the build fails loudly when vanilla changes. Nodes
    inside a match are not searched.

    >>> tree = {"left": "minecraft:a", "right": ["minecraft:a", 1]}
    >>> replace_nodes(tree, lambda node: node == "minecraft:a", 0, count=2)
    >>> tree
    {'left': 0, 'right': [0, 1]}
    """
    found = list(_find(tree, match))
    if len(found) != count:
        raise ValueError(f"Expected {count} matching node(s), found {len(found)}")
    for parent, key in found:
        parent[key] = replacement


def _find(tree: Any, match: Callable[[Any], bool]) -> Iterator[tuple[Any, Any]]:
    """Yield `(parent, key)` of every match, without descending into matches."""
    if isinstance(tree, dict):
        children = tree.items()
    elif isinstance(tree, list):
        children = enumerate(tree)
    else:
        return
    for key, child in children:
        if match(child):
            yield tree, key
        else:
            yield from _find(child, match)
