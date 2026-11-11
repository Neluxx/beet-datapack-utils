"""Resource types whose folder changed between Minecraft versions."""

from dataclasses import dataclass

from beet import JsonFile
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenConfiguredFeature,
    WorldgenFeature,
)

from .versions import Version, VersionLike

__all__ = ["CARVER", "FEATURE", "RegistryLike", "VersionedRegistry", "resolve_registry"]


@dataclass(frozen=True)
class VersionedRegistry:
    """A resource type that moved to another folder in some version.

    `default` is used before the first entry of `changes`; each entry is
    `(first_version, file_type)`.
    """

    default: type[JsonFile]
    changes: tuple[tuple[str, type[JsonFile]], ...] = ()

    def resolve(self, version: VersionLike) -> type[JsonFile]:
        """Return the file type used by `version`."""
        version = Version(version)
        file_type = self.default
        for since, candidate in sorted(self.changes, key=lambda change: Version(change[0])):
            if version >= since:
                file_type = candidate
        return file_type


RegistryLike = type[JsonFile] | VersionedRegistry

#: `worldgen/configured_carver` became `worldgen/carver` in 26.3.
CARVER = VersionedRegistry(WorldgenConfiguredCarver, (("26.3", WorldgenCarver),))

#: `worldgen/configured_feature` became `worldgen/feature` in 26.3.
FEATURE = VersionedRegistry(WorldgenConfiguredFeature, (("26.3", WorldgenFeature),))


def resolve_registry(registry: RegistryLike, version: VersionLike) -> type[JsonFile]:
    """Return the file type for `version`, accepting plain beet file types too."""
    if isinstance(registry, VersionedRegistry):
        return registry.resolve(version)
    return registry
