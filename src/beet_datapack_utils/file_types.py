"""File types whose folder moved between Minecraft versions."""

from dataclasses import dataclass

from beet import JsonFile
from beet.contrib.worldgen import (
    WorldgenCarver,
    WorldgenConfiguredCarver,
    WorldgenConfiguredFeature,
    WorldgenFeature,
)

__all__ = ["CARVER", "FEATURE", "Moved"]


@dataclass(frozen=True)
class Moved:
    """A file type that moved from `before` to `after` in version `since`.

    Pass it to `Target.patch` like a normal beet file type.
    """

    before: type[JsonFile]
    after: type[JsonFile]
    since: str

    def for_version(self, version: str) -> type[JsonFile]:
        """Return the file type used by `version`.

        >>> CARVER.for_version("26.3") is WorldgenCarver
        True
        """
        return self.after if _parse_version(version) >= _parse_version(self.since) else self.before


#: `worldgen/configured_carver` became `worldgen/carver` in 26.3.
CARVER = Moved(WorldgenConfiguredCarver, WorldgenCarver, since="26.3")

#: `worldgen/configured_feature` became `worldgen/feature` in 26.3.
FEATURE = Moved(WorldgenConfiguredFeature, WorldgenFeature, since="26.3")


def _parse_version(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.split("."))
    except ValueError:
        raise ValueError(f"Invalid release version {version!r}, expected e.g. '1.21.9'") from None
