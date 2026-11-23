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
- **Overlays:** add one for each version that changed a file you patch. Each key in `overlay_versions` must match a `directory` in `data_pack.overlays`, otherwise the build fails.
- **Pack formats:** the library doesn't set them. Set them in `data_pack` as you normally would in beet. If you leave them out, beet uses the format of the newest Minecraft version it knows.
- **Versions:** only release versions like `1.21.9` or `26.3` work. Snapshots and pre-releases (`25w45a`, `1.21.9-pre1`) don't. Always quote them: YAML reads `1.20` as the number `1.2`. The exact release is loaded: `"1.19"` means 1.19, not 1.19.4.
- **Pipeline:** `src.plugins.canyon` refers to `src/plugins/canyon.py` in your project. That file must contain a `beet_default(ctx)` function.

## Writing a plugin

Loop over `targets(ctx)`. You get one `Target` for the base pack and one for each overlay. `target.patch` copies the vanilla file of the target's version, lets you edit its JSON and writes it into the target's pack:

```python
from beet import Context

from beet_datapack_utils import CARVER, targets, worldgen_config


def beet_default(ctx: Context):
    for target in targets(ctx):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
```

## Helpers

Everything below can be imported directly from `beet_datapack_utils`.

### Targets

| Name | Description |
| --- | --- |
| `targets(ctx)` | Returns one `Target` for the base pack and one for each overlay. Raises `KeyError` if `meta.base_version` is missing or an overlay directory isn't configured, `TypeError` if a version isn't quoted. |
| `Target.pack` | The output pack of this target. Use it to add your own files, e.g. `target.pack[Function]["my:tick"] = Function([...])`. |
| `Target.version` | The target's Minecraft version, e.g. `"26.3"` |
| `Target.patch(file_type, name)` | Copies a vanilla file, yields its JSON for editing and writes it into `pack`. Nothing is written if the block raises an error. Raises `KeyError` if the file doesn't exist in the target's version. |
| `Target.inline_density_function(node)` | If `node` is an ID, returns a copy of that vanilla density function. Otherwise returns `node` unchanged. |

### File types

`file_type` can be any beet file type, e.g. `WorldgenNoise` or `WorldgenNoiseSettings`. For files whose folder moved between versions, use one of these:

| Name | Description |
| --- | --- |
| `CARVER` | `worldgen/configured_carver` before 26.3, `worldgen/carver` from 26.3 on |
| `FEATURE` | `worldgen/configured_feature` before 26.3, `worldgen/feature` from 26.3 on |
| `Moved(before, after, since)` | Defines your own moved file type, e.g. `Moved(OldType, NewType, since="27.1")` |

### Fields

| Name | Description |
| --- | --- |
| `worldgen_config(data)` | Returns the settings object of a carver or feature (the `config` wrapper was removed in 26.3) |
| `set_range(config, name, minimum, maximum)` | Sets the bounds of the uniform provider `config[name]`. Handles the `value` wrapper used before 1.20.5 and both `max_exclusive` and `max_inclusive`. Raises `ValueError` if the field isn't a range. |
| `resolve_key(data, *candidates)` | Returns the first key that exists, for renamed fields, e.g. `resolve_key(noise, "base_octave", "firstOctave")`. Raises `KeyError` if none of them exist. |

### Density functions

| Name | Description |
| --- | --- |
| `is_reference(node, function_id)` | `True` if `node` references `function_id`, directly or through cache/interpolation wrappers |
| `replace_nodes(tree, match, replacement, count=n)` | Replaces every node below `tree` for which `match(node)` is `True`. Exactly `count` nodes must match, otherwise it raises `ValueError` and changes nothing, so your build fails when vanilla changes. Nodes inside a match are not searched. |

## Examples

Change a range and a renamed field:

```python
with target.patch(CARVER, "minecraft:cave") as cave:
    config = worldgen_config(cave)
    set_range(config, "horizontal_radius_multiplier", 0.8, 1.5)
    room = resolve_key(config, "room_vertical_radius_multiplier", "yScale")
    set_range(config, room, 0.1, 0.9)
```

Replace a node in a density function:

```python
NOODLE = "minecraft:overworld/caves/noodle"

with target.patch(WorldgenNoiseSettings, "minecraft:overworld") as settings:
    router = settings["noise_router"]
    router["final_density"] = target.inline_density_function(router["final_density"])
    replace_nodes(router["final_density"], lambda node: node == NOODLE, 1, count=1)
```
