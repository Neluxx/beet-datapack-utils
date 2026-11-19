"""Patch vanilla files for the base pack and every overlay."""

from collections.abc import Iterator
from contextlib import contextmanager
from functools import cached_property
from typing import Any

from beet import Context, DataPack, JsonFile
from beet.contrib.vanilla import Vanilla
from beet.contrib.worldgen import WorldgenDensityFunction

from .file_types import Moved

__all__ = ["Target", "targets"]


def targets(ctx: Context) -> list[Target]:
    """Return one `Target` for the base pack and one for each overlay.

    Versions come from `meta.base_version` and `meta.overlay_versions`
    (overlay directory -> version) in the beet config.

        def beet_default(ctx: Context):
            for target in targets(ctx):
                ...
    """
    meta = ctx.meta
    if "base_version" not in meta:
        raise KeyError("Missing `meta.base_version` in the beet config")

    result = [Target(ctx, ctx.data, str(meta["base_version"]))]
    for directory, version in meta.get("overlay_versions", {}).items():
        result.append(Target(ctx, ctx.data.overlays[directory], str(version)))
    return result


class Target:
    """One output pack (the base pack or an overlay) and its Minecraft version."""

    def __init__(self, ctx: Context, pack: DataPack, version: str):
        self.pack = pack
        self.version = version
        self._ctx = ctx

    @contextmanager
    def patch(self, file_type: type[JsonFile] | Moved, name: str) -> Iterator[Any]:
        """Copy a vanilla file, let the caller edit its JSON, then write it into `pack`.

        Nothing is written if the block raises.

            with target.patch(CARVER, "minecraft:canyon") as carver:
                worldgen_config(carver)["probability"] = 0
        """
        if isinstance(file_type, Moved):
            file_type = file_type.for_version(self.version)
        file = self._vanilla_copy(file_type, name)
        yield file.data
        self.pack[file_type][name] = file

    def inline_density_function(self, node: Any) -> Any:
        """Return a copy of the vanilla density function if `node` is an id, else `node`.

        26.3 moved most noise router functions into separate files. Inlining
        keeps a patch local to one noise settings file.
        """
        if isinstance(node, str):
            return self._vanilla_copy(WorldgenDensityFunction, node).data
        return node

    def _vanilla_copy(self, file_type: type[JsonFile], name: str) -> JsonFile:
        try:
            return self._vanilla[file_type][name].copy()
        except KeyError:
            raise KeyError(
                f"{name} ({file_type.__name__}) not found in vanilla {self.version}"
            ) from None

    @cached_property
    def _vanilla(self) -> DataPack:
        # Loaded on first use, so packs that never read vanilla build offline.
        # beet caches the Vanilla service and its releases for the whole build.
        return self._ctx.inject(Vanilla).releases[self.version].mount("data").data
