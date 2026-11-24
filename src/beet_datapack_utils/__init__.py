"""Helpers for building multi-version Minecraft datapacks with beet.

A build has a base pack and overlays, each for one Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config).
`targets(ctx)` returns one `Target` per pack; `Target.patch` copies a vanilla
file of that version, lets you edit it and writes it back.
"""

from .fields import resolve_key, set_range, worldgen_config
from .file_types import CARVER, FEATURE
from .target import Target, targets

__all__ = [
    "CARVER",
    "FEATURE",
    "Target",
    "resolve_key",
    "set_range",
    "targets",
    "worldgen_config",
]
