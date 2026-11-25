# Usage

## Configuring `beet.yml`

The library reads two keys from `meta`:

| Key | Required | Description |
| --- | --- | --- |
| `base_version` | Yes | Minecraft version of the base pack |
| `overlay_versions` | No | Overlay directory → Minecraft version |

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

- **Base version:** use the oldest version you support. Every version that no overlay covers uses the base pack.
- **Overlays:** add one for each version that changed a file you edit. Each key in `overlay_versions` must also be a `directory` in `data_pack.overlays`, otherwise the build fails.
- **Pack formats:** set them in `data_pack` as usual. The library doesn't touch them.
- **Versions:** only releases like `"1.21.9"` or `"26.3"`, no snapshots or pre-releases. Always quote them, because YAML reads `1.20` as the number `1.2`. `"1.19"` means exactly 1.19, not 1.19.4.
- **Pipeline:** `src.plugins.canyon` is the file `src/plugins/canyon.py`, which must contain a `beet_default(ctx)` function.

## Writing a plugin

Loop over `versioned_packs(ctx)` and edit files with `pack.edit`:

```python
from beet import Context

from beet_datapack_utils import CARVER, get_config, versioned_packs


def beet_default(ctx: Context):
    for pack in versioned_packs(ctx):
        with pack.edit(CARVER, "minecraft:canyon") as canyon:
            get_config(canyon)["probability"] = 0
```

The loop runs once for the base pack and once per overlay. Inside the `with` block, `canyon` is the JSON of the file as a `dict`. When the block ends, the file is written into the pack.

## API

Everything is imported from `beet_datapack_utils`.

### Packs

| Name | Description |
| --- | --- |
| `versioned_packs(ctx)` | Returns a `VersionedPack` for the base pack and one for each overlay. |
| `VersionedPack.data` | The beet `DataPack` to write into, e.g. `pack.data[Function]["my:tick"] = Function([...])`. |
| `VersionedPack.version` | The Minecraft version, e.g. `"26.3"`. |
| `VersionedPack.edit(file_type, name)` | Yields the JSON of a file for editing and writes it into `data`. Starts from the file in `data` if it is already there (your own files or an earlier edit), otherwise from vanilla. Nothing is written if the block raises an error. |

Vanilla is only downloaded when `edit` needs it.

### File types

`edit` takes any beet file type, e.g. `WorldgenNoise`. For files whose folder moved, use:

| Name | Before 26.3 | From 26.3 on |
| --- | --- | --- |
| `CARVER` | `worldgen/configured_carver` | `worldgen/carver` |
| `CARVER_TAG` | `tags/worldgen/configured_carver` | `tags/worldgen/carver` |
| `FEATURE` | `worldgen/configured_feature` | `worldgen/feature` |
| `FEATURE_TAG` | `tags/worldgen/configured_feature` | `tags/worldgen/feature` |

### Fields

| Name | Description |
| --- | --- |
| `get_config(data)` | Returns the settings of a carver or feature: `data["config"]` before 26.3, `data` itself from 26.3 on. |
| `set_uniform(config, name, minimum, maximum)` | Sets the bounds of the uniform range `config[name]`. Works for int and float ranges and the format before 1.20.5. |
| `find_key(data, *keys)` | Returns the first of `keys` that exists in `data`. Use it for renamed fields. |

### Errors

| Error | When |
| --- | --- |
| `KeyError` | A file doesn't exist in that version, or `find_key` finds none of the keys. |
| `TypeError` | A version in `beet.yml` isn't quoted. |
| `ValueError` | `meta.base_version` is missing, a version isn't a release or isn't a known release, an overlay directory isn't in `data_pack.overlays`, or `set_uniform` is used on a field that isn't a uniform range. |

## Examples

Change ranges and a renamed field of a carver:

```python
for pack in versioned_packs(ctx):
    with pack.edit(CARVER, "minecraft:cave") as cave:
        config = get_config(cave)
        set_uniform(config, "horizontal_radius_multiplier", 0.8, 1.5)
        room = find_key(config, "room_vertical_radius_multiplier", "yScale")
        set_uniform(config, room, 0.1, 0.9)
```

Edit a file type whose folder didn't move:

```python
from beet.contrib.worldgen import WorldgenNoise

for pack in versioned_packs(ctx):
    with pack.edit(WorldgenNoise, "minecraft:temperature") as noise:
        noise[find_key(noise, "base_octave", "firstOctave")] = -9
```

Add your own files to every pack:

```python
from beet import Function, FunctionTag

for pack in versioned_packs(ctx):
    pack.data[Function]["my_pack:tick"] = Function(["gamemode survival @a"])
    pack.data["minecraft:tick"] = FunctionTag({"values": ["my_pack:tick"]})
```
