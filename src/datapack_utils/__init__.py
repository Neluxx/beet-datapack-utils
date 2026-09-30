"""Helper functions for Minecraft datapacks using beet.

A datapack build has a base pack and overlays, each for a Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config). These
helpers copy the matching vanilla files, hide format differences between
versions and write the patched files back.
"""

from .fields import octave_key, provider, resolve_key, set_range, worldgen_config
from .registries import CARVER, FEATURE, RegistryLike, VersionedRegistry, resolve_registry
from .versions import Version, VersionLike, parse_version

__all__ = [
    "CARVER",
    "FEATURE",
    "RegistryLike",
    "Version",
    "VersionLike",
    "VersionedRegistry",
    "octave_key",
    "parse_version",
    "provider",
    "resolve_key",
    "resolve_registry",
    "set_range",
    "worldgen_config",
]
