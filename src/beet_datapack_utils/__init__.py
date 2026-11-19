"""Helpers for building multi-version Minecraft datapacks with beet.

A build has a base pack and overlays, each for one Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config).
`targets(ctx)` returns one `Target` per pack; `Target.patch` copies a vanilla
file of that version, lets you edit it and writes it back.
"""

from .density import WRAPPER_TYPES, is_reference, unwrap
from .fields import octave_key, provider, resolve_key, set_range, worldgen_config
from .file_types import CARVER, FEATURE, Moved
from .target import Target, targets
from .trees import find_nodes, replace_nodes

__all__ = [
    "CARVER",
    "FEATURE",
    "WRAPPER_TYPES",
    "Moved",
    "Target",
    "find_nodes",
    "is_reference",
    "octave_key",
    "provider",
    "replace_nodes",
    "resolve_key",
    "set_range",
    "targets",
    "unwrap",
    "worldgen_config",
]
