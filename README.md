# beet-datapack-utils

[![CI](https://github.com/Neluxx/beet-datapack-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/Neluxx/beet-datapack-utils/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/beet-datapack-utils)](https://pypi.org/project/beet-datapack-utils/)
[![Python](https://img.shields.io/pypi/pyversions/beet-datapack-utils)](https://pypi.org/project/beet-datapack-utils/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/Neluxx/beet-datapack-utils/blob/main/LICENSE)

A Python library with helpers for building multi-version Minecraft datapacks with [beet](https://github.com/mcbeet/beet).

Minecraft changes the datapack format regularly: folders are renamed, fields move or disappear. To support several Minecraft versions from one build, you need a base pack plus one overlay per version, and each of them needs its own patched copy of every vanilla file you change.

This library does that work for you. For the base pack and every overlay, it copies the matching vanilla file, smooths over the format differences and writes the patched file back. Your plugin only describes *what* to change.

## Features

- **One plugin for all versions:** loop over the base pack and all overlays with `targets(ctx)`.
- **Vanilla patching:** copy, edit and write a vanilla file in a single `with` block. Vanilla is only downloaded when needed.
- **Version differences:** helpers for moved folders and renamed or restructured fields.
- **Safe density function edits:** search and replace nodes in JSON trees, and fail the build if the vanilla structure has changed.

## Quick start

**Requirements:** Python 3.14 or newer and a package manager. [uv](https://docs.astral.sh/uv/) is recommended.

**1. Install** the package in your datapack project:

```bash
uv add beet-datapack-utils
```

**2. Configure `beet.yml`.** Set the Minecraft version of the base pack and of each overlay:

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

**3. Write a plugin** in e.g. `src/plugins/canyon.py`:

```python
from beet import Context

from beet_datapack_utils import CARVER, targets, worldgen_config


def beet_default(ctx: Context):
    for target in targets(ctx):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
```

**4. Build** the datapack:

```bash
uv run beet build
```

This one plugin disables canyons in every version. Before 26.3 the file is `worldgen/configured_carver/canyon.json` and has a `config` object. From 26.3 on it is `worldgen/carver/canyon.json` and has no `config` object.

## Documentation

| Guide | Contents |
| --- | --- |
| [Installation](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/INSTALLATION.md) | Requirements, installing, building and updating |
| [Usage](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/USAGE.md) | Configuring `beet.yml` and an overview of all helpers |
| [Development](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/DEVELOPMENT.md) | Setup, tests, conventions and releasing |
| [Changelog](https://github.com/Neluxx/beet-datapack-utils/blob/main/CHANGELOG.md) | Changes in each release |
