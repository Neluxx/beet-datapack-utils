# Usage

## Configuring `beet.yml`

The library reads two keys from `meta`:

| Key | Required | Description |
| --- | --- | --- |
| `base_version` | Yes | Minecraft version of the base pack |
| `overlay_versions` | No | Mapping of overlay directory to Minecraft version |

```yaml
pipeline:
  - src.plugins.canyon

meta:
  base_version: "1.21.9"
  overlay_versions:
    v26_3: "26.3"

data_pack:
  min_format: 88   # 1.21.9
  max_format: 121  # 26.3
  overlays:
    - directory: v26_3
      min_format: 121
      max_format: 121
```

- **Base version:** use the oldest version you support. The base pack is built from that version's vanilla files, but every version in its format range that no overlay covers loads it.
- **Overlays:** add one for each version that changed a file you patch. Each key in `overlay_versions` should match a `directory` in `data_pack.overlays`. If a directory isn't listed there, it gets beet's default pack format.
- **Pack formats:** the library doesn't set them. Set them in `data_pack` as you normally would in beet. If you leave them out, beet uses the format of the newest Minecraft version it knows.
- **Versions:** only release versions like `1.21.9` or `26.3` work. Snapshots and pre-releases (`25w45a`, `1.21.9-pre1`) don't.
- **Pipeline:** `src.plugins.canyon` refers to `src/plugins/canyon.py` in your project. That file must contain a `beet_default(ctx)` function.

## Writing a plugin

Inject `Targets` and loop over it. You get one `Target` for the base pack and one for each overlay:

```python
from beet import Context

from beet_datapack_utils import CARVER, Targets, worldgen_config


def beet_default(ctx: Context):
    for target in ctx.inject(Targets):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
```

## Helpers

Everything below can be imported directly from `beet_datapack_utils`.

### Targets

| Name | Description |
| --- | --- |
| `Targets` | Beet service (`ctx.inject(Targets)`) that yields one `Target` for the base pack and one for each overlay. All plugins in a build share it, so each vanilla version is loaded only once. Supports `len()`. Raises `KeyError` if `meta.base_version` is missing. |
| `Target.pack` | The output pack this target writes to |
| `Target.version` | The target's Minecraft `Version` |
| `Target.directory` | The overlay directory, or `None` for the base pack |
| `Target.is_overlay` | `True` for overlays, `False` for the base pack |
| `Target.at_least(version)` | `True` if the target's version is `version` or newer |
| `Target.patch(registry, name)` | Context manager that copies a vanilla file, yields its JSON for editing and writes it into the target pack. Nothing is written if the block raises an error. |
| `Target.copy(registry, name)` | Returns an independent copy of a vanilla file. Raises `KeyError` if the file doesn't exist in the target's version. |
| `Target.write(registry, name, file)` | Writes a file into the target pack |
| `Target.file_type(registry)` | The beet file type that `registry` resolves to for the target's version |
| `Target.vanilla` | The vanilla data pack for the target's version. It is downloaded the first time you access it. |
| `Target.inline_density_function(node)` | If `node` is an ID, returns a copy of that vanilla density function. Otherwise returns `node` unchanged. |

### Registries

You can pass any beet file type (for example, `WorldgenNoise`) as `registry`. For resources whose folder moved between versions, pass a `VersionedRegistry` instead.

| Name | Description |
| --- | --- |
| `CARVER` | `worldgen/configured_carver` before 26.3, `worldgen/carver` from 26.3 on |
| `FEATURE` | `worldgen/configured_feature` before 26.3, `worldgen/feature` from 26.3 on |
| `VersionedRegistry(default, changes)` | Defines your own moved registry. Example: `VersionedRegistry(OldType, (("26.3", NewType),))` |
| `resolve_registry(registry, version)` | Returns the file type a registry uses in a given version |

### Fields

| Name | Description |
| --- | --- |
| `worldgen_config(data)` | Returns the settings object of a carver or feature (the `config` wrapper was removed in 26.3) |
| `provider(config, name)` | Returns the int/float provider `name`, unwrapping the `value` object used before 1.20.5. Raises `TypeError` if the field is a constant. |
| `set_range(provider, minimum, maximum)` | Sets `min_inclusive` and either `max_exclusive` or `max_inclusive`, whichever the provider uses. Raises `KeyError` if the provider isn't a range. |
| `resolve_key(data, *candidates)` | Returns the first key that exists, for renamed fields (e.g. `yScale` → `room_vertical_radius_multiplier`). Raises `KeyError` if none of them exist. |
| `octave_key(noise)` | Returns `firstOctave` or `base_octave`, the name used from 26.3 on |

### JSON trees and density functions

| Name | Description |
| --- | --- |
| `find_nodes(tree, match)` | Yields every node below `tree` (depth first, not including `tree` itself) for which `match(node)` returns `True` |
| `replace_nodes(tree, match, replacement, expected=None)` | Replaces matching nodes below `tree` and returns how many it replaced. It doesn't descend into replaced nodes. If you pass `expected` and the number of matches differs, it raises `ValueError` and changes nothing. |
| `unwrap(node)` | Removes caching and interpolation wrappers (`cache_once`, `interpolated`, …) from a density function |
| `is_reference(node, function_id)` | `True` if `node` references `function_id`, directly or through wrappers |
| `WRAPPER_TYPES` | The set of density function types that `unwrap` removes |

### Versions

| Name | Description |
| --- | --- |
| `Version(version)` | A Minecraft release version that compares with other versions and plain strings, e.g. `Version("1.21.9") < "26.3"`. `1.21` and `1.21.0` count as equal. Raises `ValueError` for snapshots and pre-releases. |
| `parse_version(version)` | Same as `Version(version)` |
| `VersionLike` | Type alias for `Version \| str` |
| `RegistryLike` | Type alias for a beet file type or a `VersionedRegistry` |
