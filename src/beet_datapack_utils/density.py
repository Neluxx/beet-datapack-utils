"""Helpers for density functions."""

from typing import Any

__all__ = ["WRAPPER_TYPES", "is_reference", "unwrap"]

#: Density function types that only wrap their input for caching/interpolation.
WRAPPER_TYPES = frozenset(
    {
        "minecraft:cache_2d",
        "minecraft:cache_all_in_cell",
        "minecraft:cache_once",
        "minecraft:flat_cache",
        "minecraft:interpolated",
    }
)


def unwrap(node: Any) -> Any:
    """Strip caching/interpolation wrappers and return the wrapped function.

    The wrapped function is stored in `argument` before 26.3 and in `input`
    since 26.3.
    """
    while isinstance(node, dict) and node.get("type") in WRAPPER_TYPES:
        inner = node.get("input", node.get("argument"))
        if inner is None:
            break
        node = inner
    return node


def is_reference(node: Any, function_id: str) -> bool:
    """Return True if `node` references `function_id`, possibly through wrappers.

    >>> is_reference({"type": "minecraft:cache_once", "argument": "minecraft:a"}, "minecraft:a")
    True
    """
    return unwrap(node) == function_id
