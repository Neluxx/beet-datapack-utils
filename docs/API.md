# API reference

Everything listed here can be imported from `beet_datapack_utils`.

## Targets

| Name | Description |
| --- | --- |
| `Targets` | Beet service (`ctx.inject(Targets)`) yielding a `Target` for the base pack and every overlay from `meta.base_version` and `meta.overlay_versions`. Shared by all plugins of a build, so each vanilla version is mounted only once. Supports `len()`. Raises `KeyError` if `meta.base_version` is missing. |
| `Target.pack` / `.version` / `.directory` | Output pack, its `Version` and the overlay directory (`None` for the base pack). |
| `Target.is_overlay` | `True` for overlays, `False` for the base pack. |
| `Target.at_least(version)` | `True` if the target is that version or newer. |
| `Target.patch(registry, name)` | Context manager: copies a vanilla file, yields its JSON for editing and writes it to the target pack. Nothing is written if the block raises. |
| `Target.copy(registry, name)` / `.write(registry, name, file)` | The two halves of `patch`, for more control. `copy` returns an independent copy of the vanilla file and raises `KeyError` if it does not exist in the target's version. |
| `Target.file_type(registry)` | The beet file type that `registry` resolves to for the target's version. |
| `Target.vanilla` | The mounted vanilla data pack of the target's version. Vanilla is only downloaded on first access, so packs that just write their own files (e.g. functions per overlay) build offline. |
| `Target.inline_density_function(node)` | Returns a copy of the referenced vanilla density function if `node` is an id, otherwise `node` itself. |

## Registries

`registry` can be any beet file type (e.g. `WorldgenNoise`) or a `VersionedRegistry` for resources that moved to another folder:

| Name | Before 26.3 | Since 26.3 |
| --- | --- | --- |
| `CARVER` | `worldgen/configured_carver` | `worldgen/carver` |
| `FEATURE` | `worldgen/configured_feature` | `worldgen/feature` |

Define your own with `VersionedRegistry(default, (("26.3", NewFileType),))`, or resolve one manually with `resolve_registry(registry, version)`.

## Fields

| Name | Description |
| --- | --- |
| `worldgen_config(data)` | Settings object of a carver or feature (the `config` wrapper was removed in 26.3). |
| `provider(config, name)` | Int/float provider `name`, unwrapping the pre-1.20.5 `value` object. Raises `TypeError` if the field is a constant number instead of a provider object. |
| `set_range(provider, minimum, maximum)` | Sets `min_inclusive` and `max_exclusive` or `max_inclusive`, whichever the provider uses. Raises `KeyError` if the provider has no such bounds. |
| `resolve_key(data, *candidates)` | First existing key, for renamed fields such as `yScale` → `room_vertical_radius_multiplier`. Raises `KeyError` if none exists. |
| `octave_key(noise)` | `firstOctave` or `base_octave` (renamed in 26.3). |

## JSON trees and density functions

| Name | Description |
| --- | --- |
| `find_nodes(tree, match)` | Yields every node below `tree` (depth first, not `tree` itself) for which `match` returns `True`. |
| `replace_nodes(tree, match, replacement, expected=None)` | Replaces matching nodes below `tree` and returns the count. Does not descend into replaced nodes. The same `replacement` object is inserted at every match. With `expected`, raises `ValueError` and changes nothing if the count differs, so a changed vanilla structure fails the build instead of silently doing nothing. |
| `unwrap(node)` | Strips caching and interpolation wrappers (`cache_once`, `interpolated`, …) from a density function. |
| `is_reference(node, function_id)` | `True` if `node` references `function_id`, directly or through wrappers. |
| `WRAPPER_TYPES` | The density function types removed by `unwrap`. |

## Versions

| Name | Description |
| --- | --- |
| `Version(version)` / `parse_version(version)` | A Minecraft release version that compares with other versions and plain strings: `Version("1.21.9") < "26.3"`. `1.21` and `1.21.0` are equal. Raises `ValueError` for snapshots and pre-releases. |
| `VersionLike` | Type alias for anything accepted as a version (`Version` or `str`). |
| `RegistryLike` | Type alias for a beet file type or a `VersionedRegistry`. |
