"""Minecraft version parsing and comparison."""

from functools import total_ordering

__all__ = ["Version", "VersionLike", "parse_version"]


@total_ordering
class Version:
    """A release version like `1.21.9` or `26.3`, comparable with strings.

    >>> Version("26.3") >= "26.3"
    True
    >>> Version("1.20.5") < Version("1.21")
    True
    """

    __slots__ = ("parts",)

    def __init__(self, version: VersionLike):
        if isinstance(version, Version):
            self.parts: tuple[int, ...] = version.parts
            return
        try:
            parts = tuple(int(part) for part in version.split("."))
        except ValueError:
            raise ValueError(f"Invalid release version {version!r}") from None
        # Treat "1.21" and "1.21.0" as the same version.
        while len(parts) > 1 and parts[-1] == 0:
            parts = parts[:-1]
        self.parts = parts

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            try:
                other = Version(other)
            except ValueError:
                return False
        if isinstance(other, Version):
            return self.parts == other.parts
        return NotImplemented

    def __lt__(self, other: VersionLike) -> bool:
        return self.parts < Version(other).parts

    def __hash__(self) -> int:
        return hash(self.parts)

    def __str__(self) -> str:
        return ".".join(map(str, self.parts))

    def __repr__(self) -> str:
        return f"Version({str(self)!r})"


VersionLike = Version | str


def parse_version(version: VersionLike) -> Version:
    """Parse a release version string like `1.20.5`."""
    return Version(version)
