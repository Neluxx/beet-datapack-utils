"""File types whose folder moved between Minecraft versions."""

from dataclasses import dataclass

from beet import JsonFile
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenConfiguredFeature,
    WorldgenFeature,
)
from beet.core.utils import split_version

__all__ = ["CARVER", "FEATURE"]


@dataclass(frozen=True)
class MovedFileType:
    """A file type that is `old` before version `since` and `new` from then on."""

    old: type[JsonFile]
    new: type[JsonFile]
    since: str

    def for_version(self, version: str) -> type[JsonFile]:
        """Return the file type that `version` uses.

        >>> CARVER.for_version("26.3") is WorldgenCarver
        True
        """
        return self.new if split_version(version) >= split_version(self.since) else self.old


#: `worldgen/configured_carver` before 26.3, `worldgen/carver` from 26.3 on.
CARVER = MovedFileType(WorldgenConfiguredCarver, WorldgenCarver, since="26.3")

#: `worldgen/configured_feature` before 26.3, `worldgen/feature` from 26.3 on.
FEATURE = MovedFileType(WorldgenConfiguredFeature, WorldgenFeature, since="26.3")
