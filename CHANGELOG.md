# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed
- **Breaking:** `targets(ctx)` raises `KeyError` if a directory in `meta.overlay_versions` is missing in `data_pack.overlays` instead of creating a new overlay
- **Breaking:** `targets(ctx)` raises `TypeError` if a version isn't a string, e.g. an unquoted `1.20`

### Deprecated

### Removed

### Fixed
- `Target.patch` starts from the file already in the pack, so several plugins can patch the same file
- Load the exact vanilla release. beet looks up releases by prefix, so `"1.19"` loaded 1.19.4
- A vanilla version that can't be loaded is no longer reported as a missing file

### Security

### Dependencies

## [v0.2.0](https://github.com/Neluxx/beet-datapack-utils/releases/tag/v0.2.0) - 2026-11-21

### Changed
- **Breaking:** `ctx.inject(Targets)` is replaced by the function `targets(ctx)`
- **Breaking:** `set_range(config, name, minimum, maximum)` takes the config and the field name and replaces `set_range(provider(config, name), ...)`
- **Breaking:** `replace_nodes` requires the keyword `count` (formerly the optional `expected`) and returns nothing
- **Breaking:** `VersionedRegistry` is replaced by `Moved(before, after, since)`
- `Target.version` is a plain string
- `Target(pack, version, load_vanilla)` takes a function that loads the vanilla pack instead of the beet context

### Removed
- `Targets`, `provider`, `octave_key` (use `resolve_key(noise, "base_octave", "firstOctave")`), `find_nodes`, `unwrap`, `WRAPPER_TYPES`, `resolve_registry`, `RegistryLike`, `Version`, `VersionLike` and `parse_version`
- `Target.directory`, `Target.is_overlay`, `Target.at_least`, `Target.copy`, `Target.write`, `Target.file_type` and `Target.vanilla`

## [v0.1.0](https://github.com/Neluxx/beet-datapack-utils/releases/tag/v0.1.0) - 2026-11-17

### Added
- `Targets` service and `Target.patch` to copy, modify and write vanilla files for the base pack and every overlay
- `CARVER` and `FEATURE` registries for the 26.3 folder renames, `VersionedRegistry` for custom ones
- `worldgen_config`, `provider`, `set_range`, `resolve_key` and `octave_key` for fields that changed between versions
- `find_nodes` and `replace_nodes` for JSON trees, `unwrap` and `is_reference` for density functions
- `Version` for comparing Minecraft release versions
