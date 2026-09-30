"""Helper functions for Minecraft datapacks using beet.

A datapack build has a base pack and overlays, each for a Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config). These
helpers copy the matching vanilla files, hide format differences between
versions and write the patched files back.
"""

from .registries import CARVER, FEATURE, RegistryLike, VersionedRegistry, resolve_registry
from .versions import Version, VersionLike, parse_version

__all__ = [
    "CARVER",
    "FEATURE",
    "RegistryLike",
    "Version",
    "VersionLike",
    "VersionedRegistry",
    "parse_version",
    "resolve_registry",
]
