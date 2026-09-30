"""Helper functions for Minecraft datapacks using beet.

A datapack build has a base pack and overlays, each for a Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config). These
helpers copy the matching vanilla files, hide format differences between
versions and write the patched files back.
"""

from .density import WRAPPER_TYPES, is_reference, unwrap
from .fields import octave_key, provider, resolve_key, set_range, worldgen_config
from .registries import CARVER, FEATURE, RegistryLike, VersionedRegistry, resolve_registry
from .trees import find_nodes, replace_nodes
from .versions import Version, VersionLike, parse_version

__all__ = [
    "CARVER",
    "FEATURE",
    "WRAPPER_TYPES",
    "RegistryLike",
    "Version",
    "VersionLike",
    "VersionedRegistry",
    "find_nodes",
    "is_reference",
    "octave_key",
    "parse_version",
    "provider",
    "replace_nodes",
    "resolve_key",
    "resolve_registry",
    "set_range",
    "unwrap",
    "worldgen_config",
]
