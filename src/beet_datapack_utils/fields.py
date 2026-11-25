"""JSON fields whose name or shape changed between Minecraft versions."""

from typing import Any

__all__ = ["find_key", "get_config", "set_uniform"]


def get_config(data: dict[str, Any]) -> dict[str, Any]:
    """Return the settings of a carver or feature.

    Before 26.3 they are wrapped in a `config` object, from 26.3 on they sit
    next to `type`.

    >>> get_config({"type": "minecraft:canyon", "config": {"probability": 0.01}})
    {'probability': 0.01}
    >>> get_config({"type": "minecraft:canyon", "probability": 0.01})
    {'type': 'minecraft:canyon', 'probability': 0.01}
    """
    return data.get("config", data)


def find_key(data: dict[str, Any], *keys: str) -> str:
    """Return the first of `keys` that exists in `data`, for renamed fields.

    >>> find_key({"firstOctave": -9}, "base_octave", "firstOctave")
    'firstOctave'
    """
    for key in keys:
        if key in data:
            return key
    raise KeyError(f"None of {list(keys)} found in {sorted(data)}")


def set_uniform(config: dict[str, Any], name: str, minimum: float, maximum: float) -> None:
    """Set the bounds of the uniform range `config[name]`.

    Works with int ranges (`max_inclusive`), float ranges (`max_exclusive`)
    and the `value` wrapper used before 1.20.5.

    >>> config = {"radius": {"type": "minecraft:uniform", "min_inclusive": 2, "max_inclusive": 3}}
    >>> set_uniform(config, "radius", 2, 5)
    >>> config["radius"]
    {'type': 'minecraft:uniform', 'min_inclusive': 2, 'max_inclusive': 5}
    """
    provider = config[name]
    if isinstance(provider, dict) and isinstance(provider.get("value"), dict):
        provider = provider["value"]
    if not isinstance(provider, dict) or "min_inclusive" not in provider:
        raise ValueError(f"{name!r} is not a uniform range: {config[name]!r}")

    upper_key = "max_exclusive" if "max_exclusive" in provider else "max_inclusive"
    provider["min_inclusive"] = minimum
    provider[upper_key] = maximum
