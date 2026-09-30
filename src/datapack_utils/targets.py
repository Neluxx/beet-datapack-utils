"""Iterate over the base pack and its overlays and patch vanilla files."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from beet import Context, DataPack, JsonFile
from beet.contrib.vanilla import Vanilla
from beet.contrib.worldgen import WorldgenDensityFunction

from .registries import RegistryLike, resolve_registry
from .versions import Version, VersionLike

__all__ = ["Target", "Targets"]


@dataclass
class Target:
    """One output pack (the base pack or an overlay) and its Minecraft version."""

    pack: DataPack
    version: Version
    directory: str | None = None
    vanilla_provider: Callable[[], Vanilla] | None = field(default=None, repr=False)

    @property
    def is_overlay(self) -> bool:
        return self.directory is not None

    def at_least(self, version: VersionLike) -> bool:
        """Return True if this target's version is `version` or newer."""
        return self.version >= version

    @cached_property
    def vanilla(self) -> DataPack:
        """The vanilla data pack of this target's version (mounted once).

        Vanilla is only fetched on first access, so packs that never read
        vanilla files build without network access.
        """
        if self.vanilla_provider is None:
            raise RuntimeError("Target was created without a Vanilla provider")
        vanilla = self.vanilla_provider()
        return vanilla.releases[str(self.version)].mount("data").data

    def file_type(self, registry: RegistryLike) -> type[JsonFile]:
        """Resolve a (versioned) registry to the file type of this version."""
        return resolve_registry(registry, self.version)

    def copy(self, registry: RegistryLike, name: str) -> JsonFile:
        """Return an independent copy of the vanilla file `name`."""
        file_type = self.file_type(registry)
        try:
            return self.vanilla[file_type][name].copy()
        except KeyError:
            raise KeyError(
                f"{name} ({file_type.__name__}) not found in vanilla {self.version}"
            ) from None

    def write(self, registry: RegistryLike, name: str, file: JsonFile) -> None:
        """Write `file` as `name` into this target's pack."""
        self.pack[self.file_type(registry)][name] = file

    @contextmanager
    def patch(self, registry: RegistryLike, name: str) -> Iterator[Any]:
        """Copy a vanilla file, let the caller modify its JSON, then write it.

        Nothing is written if the block raises.

            with target.patch(CARVER, "minecraft:canyon") as carver:
                worldgen_config(carver)["probability"] = 0
        """
        file = self.copy(registry, name)
        yield file.data
        self.write(registry, name, file)

    def inline_density_function(self, node: Any) -> Any:
        """Return a copy of the referenced vanilla density function if `node` is an id.

        Useful because 26.3 moved most noise router functions into separate
        files; inlining keeps a patch local to one noise settings file.
        """
        if isinstance(node, str):
            return self.copy(WorldgenDensityFunction, node).data
        return node


class Targets:
    """Beet service yielding a `Target` for the base pack and every overlay.

    Reads `meta.base_version` and `meta.overlay_versions` (overlay directory
    -> version). Inject it with `ctx.inject(Targets)`; the instance is shared
    by all plugins of a build, so each vanilla version is mounted only once.

        def beet_default(ctx: Context):
            for target in ctx.inject(Targets):
                ...
    """

    def __init__(self, ctx: Context):
        self.ctx = ctx

    @cached_property
    def targets(self) -> list[Target]:
        meta = self.ctx.meta
        if "base_version" not in meta:
            raise KeyError("Missing `meta.base_version` in the beet config")

        def vanilla() -> Vanilla:
            # Injected lazily: creating the Vanilla service downloads the
            # version manifest. ctx.inject caches it for the whole build.
            return self.ctx.inject(Vanilla)

        targets = [Target(self.ctx.data, Version(meta["base_version"]), None, vanilla)]
        for directory, version in meta.get("overlay_versions", {}).items():
            overlay = self.ctx.data.overlays[directory]
            targets.append(Target(overlay, Version(version), directory, vanilla))
        return targets

    def __iter__(self) -> Iterator[Target]:
        return iter(self.targets)

    def __len__(self) -> int:
        return len(self.targets)
