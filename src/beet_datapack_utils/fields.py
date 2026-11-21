"""Worldgen fields whose shape or name changed between versions."""

from typing import Any

__all__ = ["resolve_key", "set_range", "worldgen_config"]

# Float providers have an exclusive upper bound, int providers an inclusive one.
_UPPER_BOUND_KEYS = ("max_exclusive", "max_inclusive")


def worldgen_config(data: dict) -> dict:
    """Return the object holding a carver's or feature's settings.

    Before 26.3 the settings are wrapped in a `config` object. Since 26.3
    they sit directly next to `type`.
    """
    config = data.get("config")
    return config if isinstance(config, dict) else data


def resolve_key(data: dict, *candidates: str) -> str:
    """Return the first key from `candidates` that exists in `data`.

    For fields that were renamed between versions:

    >>> resolve_key({"yScale": 1}, "room_vertical_radius_multiplier", "yScale")
    'yScale'
    """
    for key in candidates:
        if key in data:
            return key
    raise KeyError(f"None of {list(candidates)} found in {sorted(data)}")


def set_range(config: dict, name: str, minimum: Any, maximum: Any) -> None:
    """Set the bounds of the uniform int/float provider `config[name]`.

    Works with the `value` wrapper used before 1.20.5 and with both
    `max_exclusive` (float providers) and `max_inclusive` (int providers).

    >>> config = {"radius": {"type": "minecraft:uniform", "min_inclusive": 2, "max_inclusive": 3}}
    >>> set_range(config, "radius", 2, 5)
    >>> config["radius"]["max_inclusive"]
    5
    """
    provider, upper = _find_range(config, name)
    provider["min_inclusive"] = minimum
    provider[upper] = maximum


def _find_range(config: dict, name: str) -> tuple[dict, str]:
    """Return the uniform provider `config[name]` and the key of its upper bound."""
    node = config[name]
    if not isinstance(node, dict):
        raise ValueError(f"{name!r} is a constant ({node!r}), not a range provider")
    if isinstance(node.get("value"), dict):
        node = node["value"]
    upper = next((key for key in _UPPER_BOUND_KEYS if key in node), None)
    if "min_inclusive" not in node or upper is None:
        raise ValueError(f"{name!r} is not a range provider: {config[name]!r}")
    return node, upper
