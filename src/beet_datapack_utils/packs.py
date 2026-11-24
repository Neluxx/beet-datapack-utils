"""The base pack and its overlays, each with its Minecraft version."""

import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import cached_property
from typing import Any

from beet import Context, DataPack, JsonFile
from beet.contrib.vanilla import ReleaseRegistry, Vanilla

from .file_types import MovedFileType

__all__ = ["VersionedPack", "versioned_packs"]

# Releases like "1.21.9" or "26.3". Snapshots and pre-releases are not supported.
RELEASE_VERSION = re.compile(r"\d+(\.\d+)*")


def versioned_packs(ctx: Context) -> list[VersionedPack]:
    """Return the base pack and every overlay, each with its Minecraft version.

    The versions come from `meta.base_version` and `meta.overlay_versions`
    (overlay directory -> version) in the beet config.
    """
    meta = ctx.meta
    if "base_version" not in meta:
        raise ValueError("Missing `meta.base_version` in the beet config")

    def load_vanilla(version: str) -> DataPack:
        return _load_vanilla(ctx, version)

    # Copied first, because `directory in ctx.data.overlays` creates the overlay.
    configured_overlays = set(ctx.data.overlays)
    packs = [VersionedPack(ctx.data, _check_version(meta["base_version"]), load_vanilla)]
    for directory, version in (meta.get("overlay_versions") or {}).items():
        if directory not in configured_overlays:
            raise ValueError(f"Overlay {directory!r} is missing in `data_pack.overlays`")
        overlay = ctx.data.overlays[directory]
        packs.append(VersionedPack(overlay, _check_version(version), load_vanilla))
    return packs


class VersionedPack:
    """A data pack (the base pack or an overlay) for one Minecraft version."""

    def __init__(
        self,
        data_pack: DataPack,
        minecraft_version: str,
        load_vanilla: Callable[[str], DataPack],
    ) -> None:
        self.data_pack = data_pack
        self.minecraft_version = minecraft_version
        self._load_vanilla = load_vanilla

    @contextmanager
    def edit(self, file_type: type[JsonFile] | MovedFileType, name: str) -> Iterator[Any]:
        """Edit the JSON of a file and write it into `data_pack`.

        Starts from the file in `data_pack` if it is already there, otherwise
        from the vanilla file of `minecraft_version`. Nothing is written if
        the `with` block raises.

            with pack.edit(CARVER, "minecraft:canyon") as canyon:
                get_config(canyon)["probability"] = 0
        """
        if isinstance(file_type, MovedFileType):
            file_type = file_type.for_version(self.minecraft_version)

        file = self.data_pack[file_type].get(name)
        if file is None:
            file = self._vanilla[file_type].get(name)
        if file is None:
            raise KeyError(f"{name} ({file_type.__name__}) not found in {self.minecraft_version}")

        file = file.copy()
        yield file.data
        self.data_pack[file_type][name] = file

    @cached_property
    def _vanilla(self) -> DataPack:
        # Loaded on first use, so packs that never read vanilla build offline.
        return self._load_vanilla(self.minecraft_version)


def _check_version(version: Any) -> str:
    # YAML reads an unquoted 1.20 as the float 1.2.
    if not isinstance(version, str):
        raise TypeError(f'Version {version!r} must be quoted in the beet config, e.g. "1.20"')
    if not RELEASE_VERSION.fullmatch(version):
        raise ValueError(f'Version {version!r} is not a release, e.g. "1.21.9" or "26.3"')
    return version


def _load_vanilla(ctx: Context, version: str) -> DataPack:
    releases = ctx.inject(Vanilla).releases
    # `releases["1.19"]` matches by prefix and returns 1.19.4, so we build a
    # registry that only contains the exact release.
    entry = next((v for v in releases.manifest.data["versions"] if v["id"] == version), None)
    if entry is None:
        raise KeyError(f"Minecraft {version} not found in the version manifest")
    manifest = JsonFile({"versions": [entry]})
    exact = ReleaseRegistry(runtimes=releases.runtimes, cache=releases.cache, manifest=manifest)
    return exact[version].mount("data").data
