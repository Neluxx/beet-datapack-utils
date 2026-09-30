"""Search and replace inside JSON trees such as density functions."""

from collections.abc import Callable, Iterator
from typing import Any

__all__ = ["find_nodes", "replace_nodes"]

Matcher = Callable[[Any], bool]


def _children(tree: Any) -> list[tuple[Any, Any]]:
    if isinstance(tree, dict):
        return list(tree.items())
    if isinstance(tree, list):
        return list(enumerate(tree))
    return []


def find_nodes(tree: Any, match: Matcher) -> Iterator[Any]:
    """Yield every node below `tree` (depth first) for which `match` is True."""
    for _, child in _children(tree):
        if match(child):
            yield child
        yield from find_nodes(child, match)


def replace_nodes(
    tree: Any,
    match: Matcher,
    replacement: Any,
    expected: int | None = None,
) -> int:
    """Replace every node below `tree` for which `match` is True.

    Does not descend into replaced nodes and returns the number of
    replacements. Pass `expected` to fail loudly when vanilla changed its
    structure; nothing is modified in that case.
    """
    if expected is not None:
        found = sum(1 for _ in _matches_without_nesting(tree, match))
        if found != expected:
            raise ValueError(f"Expected {expected} matching node(s), found {found}")
    return _replace(tree, match, replacement)


def _matches_without_nesting(tree: Any, match: Matcher) -> Iterator[Any]:
    for _, child in _children(tree):
        if match(child):
            yield child
        else:
            yield from _matches_without_nesting(child, match)


def _replace(tree: Any, match: Matcher, replacement: Any) -> int:
    count = 0
    for key, child in _children(tree):
        if match(child):
            tree[key] = replacement
            count += 1
        else:
            count += _replace(child, match, replacement)
    return count
