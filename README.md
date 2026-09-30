# beet-datapack-utils

A Python library that provides helper functions for Minecraft datapacks using [beet](https://github.com/mcbeet/beet).

It is built for datapacks that support several Minecraft versions with one build.

A build has a base pack and overlays, each targeting a Minecraft version. For every one of them, the helpers copy the matching vanilla file, hide the format differences between versions and write the patched file back. The plugins only describe *what* to change.

Used by [Medium Biomes](https://github.com/Neluxx/medium-biomes), [No More Ravines](https://github.com/Neluxx/no-more-ravines), [Cleaner Rivers](https://github.com/Neluxx/cleaner-rivers), [Vanilla Caves](https://github.com/Neluxx/vanilla-caves) and [Force Survival Mode](https://github.com/Neluxx/force-survival-mode).

## Installation

Add the package to the `pyproject.toml` of your datapack. It is installed from GitHub, pinned to a release tag:

```toml
[project]
dependencies = [
    "beet>=0.119.0",
    "beet-datapack-utils",
]

[tool.uv.sources]
beet-datapack-utils = { git = "https://github.com/Neluxx/beet-datapack-utils", tag = "v1.0.0" }
```

Then run `uv lock` and build with `uv run beet build`. Note that `uvx beet` runs beet in an isolated environment without your dependencies.

## Usage

Declare the versions in `beet.yml`:

```yaml
pipeline:
  - src.plugins.canyon

meta:
  base_version: "1.21.9"
  overlay_versions:
    v26_3: "26.3"

data_pack:
  min_format: 82
  max_format: 121
  overlays:
    - directory: v26_3
      min_format: 121
      max_format: 121
```

Write a plugin:

```python
from beet import Context

from datapack_utils import CARVER, Targets, worldgen_config


def beet_default(ctx: Context):
    for target in ctx.inject(Targets):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
```

This writes `worldgen/configured_carver/canyon.json` with a `config` object to the base pack, and `worldgen/carver/canyon.json` without it to the `v26_3` overlay.

## API

### Targets

| Name | Description |
| --- | --- |
| `Targets` | Beet service (`ctx.inject(Targets)`) yielding a `Target` for the base pack and every overlay from `meta.base_version` and `meta.overlay_versions`. Shared by all plugins of a build, so each vanilla version is mounted only once. |
| `Target.pack` / `.version` / `.directory` | Output pack, its `Version` and the overlay directory (`None` for the base pack). |
| `Target.at_least(version)` | `True` if the target is that version or newer. |
| `Target.patch(registry, name)` | Context manager: copies a vanilla file, yields its JSON for editing and writes it to the target pack. Nothing is written if the block raises. |
| `Target.copy(registry, name)` / `.write(registry, name, file)` | The two halves of `patch`, for more control. |
| `Target.vanilla` | The mounted vanilla data pack of the target's version. Vanilla is only downloaded on first access, so packs that just write their own files (e.g. functions per overlay) build offline. |
| `Target.inline_density_function(node)` | Returns a copy of the referenced vanilla density function if `node` is an id, otherwise `node` itself. |

### Registries

`registry` can be any beet file type (e.g. `WorldgenNoise`) or a `VersionedRegistry` for resources that moved to another folder:

| Name | Before 26.3 | Since 26.3 |
| --- | --- | --- |
| `CARVER` | `worldgen/configured_carver` | `worldgen/carver` |
| `FEATURE` | `worldgen/configured_feature` | `worldgen/feature` |

Define your own with `VersionedRegistry(default, (("26.3", NewFileType),))`, or resolve one manually with `resolve_registry(registry, version)`.

### Fields

| Name | Description |
| --- | --- |
| `worldgen_config(data)` | Settings object of a carver or feature (the `config` wrapper was removed in 26.3). |
| `provider(config, name)` | Int/float provider `name`, unwrapping the pre-1.20.5 `value` object. |
| `set_range(provider, minimum, maximum)` | Sets `min_inclusive` and `max_exclusive` or `max_inclusive`, whichever the provider uses. |
| `resolve_key(data, *candidates)` | First existing key, for renamed fields such as `yScale` → `room_vertical_radius_multiplier`. |
| `octave_key(noise)` | `firstOctave` or `base_octave` (renamed in 26.3). |

### JSON trees and density functions

| Name | Description |
| --- | --- |
| `find_nodes(tree, match)` | Yields every nested node for which `match` returns `True`. |
| `replace_nodes(tree, match, replacement, expected=None)` | Replaces matching nodes and returns the count. With `expected`, raises and changes nothing if the count differs, so a changed vanilla structure fails the build instead of silently doing nothing. |
| `unwrap(node)` | Strips caching and interpolation wrappers (`cache_once`, `interpolated`, …) from a density function. |
| `is_reference(node, function_id)` | `True` if `node` references `function_id`, directly or through wrappers. |

### Versions

`Version("26.3")` (or `parse_version`) compares with other versions and plain strings: `Version("1.21.9") < "26.3"`.

## Examples

Write your own files into every pack, without touching vanilla:

```python
from beet import Function

for target in ctx.inject(Targets):
    target.pack[Function]["demo:tick"] = Function(["say hello"])
```

Change a noise in every version:

```python
from beet.contrib.worldgen import WorldgenNoise

for target in ctx.inject(Targets):
    with target.patch(WorldgenNoise, "minecraft:temperature") as noise:
        noise[octave_key(noise)] = -11
```

Adjust a cave carver, including the field renamed in 26.3:

```python
for target in ctx.inject(Targets):
    with target.patch(CARVER, "minecraft:cave") as carver:
        config = worldgen_config(carver)
        set_range(provider(config, "horizontal_radius_multiplier"), 0.8, 1.5)
        room = resolve_key(config, "room_vertical_radius_multiplier", "yScale")
        set_range(provider(config, room), 0.1, 0.9)
```

Replace a part of a density function and fail if vanilla changed:

```python
with target.patch(WorldgenNoiseSettings, "minecraft:overworld") as settings:
    router = settings["noise_router"]
    router["final_density"] = target.inline_density_function(router["final_density"])
    replace_nodes(
        router["final_density"],
        lambda node: node == "minecraft:overworld/caves/noodle",
        1,
        expected=1,
    )
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for commit conventions and guidelines.
