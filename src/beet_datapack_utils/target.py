"""Patch vanilla files for the base pack and every overlay."""

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import cached_property, partial
from typing import Any

from beet import Context, DataPack, JsonFile
from beet.contrib.vanilla import ReleaseRegistry, Vanilla
from beet.contrib.worldgen import WorldgenDensityFunction

from .file_types import Moved

__all__ = ["Target", "targets"]

#: Returns the vanilla data pack of a Minecraft version.
VanillaLoader = Callable[[str], DataPack]


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

    load_vanilla = partial(_load_vanilla, ctx)
    # Copied first: `in ctx.data.overlays` would create the overlay.
    configured = set(ctx.data.overlays)
    result = [Target(ctx.data, _version(meta["base_version"]), load_vanilla)]
    for directory, version in meta.get("overlay_versions", {}).items():
        if directory not in configured:
            raise KeyError(f"Overlay {directory!r} is missing in `data_pack.overlays`")
        result.append(Target(ctx.data.overlays[directory], _version(version), load_vanilla))
    return result


class Target:
    """One output pack (the base pack or an overlay) and its Minecraft version."""

    def __init__(self, pack: DataPack, version: str, load_vanilla: VanillaLoader):
        self.pack = pack
        self.version = version
        self._load_vanilla = load_vanilla

    @contextmanager
    def patch(self, file_type: type[JsonFile] | Moved, name: str) -> Iterator[Any]:
        """Copy a file, let the caller edit its JSON, then write it into `pack`.

        Starts from the file in `pack` if it already exists there, e.g. from an
        earlier patch or the project's own files, otherwise from vanilla.
        Nothing is written if the block raises.

            with target.patch(CARVER, "minecraft:canyon") as carver:
                worldgen_config(carver)["probability"] = 0
        """
        if isinstance(file_type, Moved):
            file_type = file_type.for_version(self.version)
        existing = self.pack[file_type].get(name)
        file = existing.copy() if existing else self._vanilla_copy(file_type, name)
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
        # Loaded outside the `try`, so a failed download isn't reported as a missing file.
        vanilla = self._vanilla
        try:
            return vanilla[file_type][name].copy()
        except KeyError:
            raise KeyError(
                f"{name} ({file_type.__name__}) not found in vanilla {self.version}"
            ) from None

    @cached_property
    def _vanilla(self) -> DataPack:
        # Loaded on first use, so packs that never read vanilla build offline.
        return self._load_vanilla(self.version)


def _version(value: Any) -> str:
    # YAML reads an unquoted 1.20 as the float 1.2.
    if not isinstance(value, str):
        raise TypeError(f'Version {value!r} must be quoted in the beet config, e.g. "1.20"')
    return value


def _load_vanilla(ctx: Context, version: str) -> DataPack:
    releases = ctx.inject(Vanilla).releases
    # `releases["1.19"]` matches release ids by prefix and returns 1.19.4, the
    # newest match in the manifest. A registry with only the exact release can't.
    entry = next((v for v in releases.manifest.data["versions"] if v["id"] == version), None)
    if entry is None:
        raise KeyError(f"Minecraft {version} not found in the version manifest")
    manifest = JsonFile({"versions": [entry]})
    exact = ReleaseRegistry(runtimes=releases.runtimes, cache=releases.cache, manifest=manifest)
    return exact[version].mount("data").data
