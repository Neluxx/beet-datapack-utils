"""Access to worldgen fields whose shape or name changed between versions."""

from typing import Any

__all__ = ["octave_key", "provider", "resolve_key", "set_range", "worldgen_config"]


def worldgen_config(data: dict) -> dict:
    """Return the object holding a carver's or feature's settings.

    Before 26.3 the settings are wrapped in a `config` object. Since 26.3
    they sit directly on the root object next to `type`.
    """
    config = data.get("config")
    return config if isinstance(config, dict) else data


def resolve_key(data: dict, *candidates: str) -> str:
    """Return the first key from `candidates` that exists in `data`.

    Used for fields that were renamed between versions, e.g.
    `resolve_key(config, "room_vertical_radius_multiplier", "yScale")`.
    """
    for key in candidates:
        if key in data:
            return key
    raise KeyError(f"None of {list(candidates)} found in {sorted(data)}")


def octave_key(noise: dict) -> str:
    """Return the first-octave field of a noise (`firstOctave` became `base_octave` in 26.3)."""
    return resolve_key(noise, "base_octave", "firstOctave")


def provider(config: dict, name: str) -> dict:
    """Return the int/float provider `name`, unwrapping the pre-1.20.5 `value` object.

    Before 1.20.5 a uniform provider looked like
    `{"type": "uniform", "value": {"min_inclusive": 0.7, "max_exclusive": 1.4}}`.
    Since then the bounds sit directly next to `type`.
    """
    node = config[name]
    if not isinstance(node, dict):
        raise TypeError(f"{name!r} is a constant ({node!r}), not a provider object")
    value = node.get("value")
    return value if isinstance(value, dict) else node


def set_range(node: dict, minimum: Any, maximum: Any) -> None:
    """Set the bounds of a uniform-like provider.

    Writes `min_inclusive` and whichever upper bound the provider uses:
    `max_exclusive` (float providers) or `max_inclusive` (int providers).
    """
    upper: str | None = next(
        (key for key in ("max_exclusive", "max_inclusive") if key in node), None
    )
    if upper is None or "min_inclusive" not in node:
        raise KeyError(f"Not a range provider: {node!r}")
    node["min_inclusive"] = minimum
    node[upper] = maximum
