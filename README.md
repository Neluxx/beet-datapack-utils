# beet-datapack-utils

A Python library that provides helper functions for Minecraft datapacks using [beet](https://github.com/mcbeet/beet).

Minecraft keeps changing the data format of datapacks: folders get renamed, fields move or are removed. A datapack that supports several Minecraft versions with one build needs a base pack and an overlay for each version, and each of them needs its own copy of every vanilla file it changes.

This library takes care of that. For the base pack and every overlay, it copies the matching vanilla file, hides the format differences between the versions and writes the patched file back. Your plugins only describe *what* to change:

```python
from beet import Context

from beet_datapack_utils import CARVER, Targets, worldgen_config


def beet_default(ctx: Context):
    for target in ctx.inject(Targets):
        with target.patch(CARVER, "minecraft:canyon") as carver:
            worldgen_config(carver)["probability"] = 0
```

This one plugin disables canyons in every version, even though the file is `worldgen/configured_carver/canyon.json` with a `config` object before 26.3 and `worldgen/carver/canyon.json` without it since 26.3.

## Features

- **One plugin for all versions:** iterate over the base pack and all overlays with `Targets`.
- **Vanilla patching:** copy, edit and write vanilla files in one `with` block. Each vanilla version is downloaded only once, and only when needed.
- **Version differences:** helpers for moved registries and renamed or restructured fields.
- **Safe edits of density functions:** search and replace nodes in JSON trees, and fail the build if the vanilla structure changed.

## Quick start

Requires Python 3.14+ and beet 0.119.0+.

```bash
uv add beet-datapack-utils
```

## Documentation

| Topic | Description |
| --- | --- |
| [Installation](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/INSTALLATION.md) | Requirements and adding the package to your datapack |
| [API reference](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/API.md) | All public classes and functions |
| [Development](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/DEVELOPMENT.md) | Setting up the project, running tests and releasing |
| [Contributing](https://github.com/Neluxx/beet-datapack-utils/blob/main/docs/CONTRIBUTING.md) | Commit conventions and guidelines |
| [Changelog](https://github.com/Neluxx/beet-datapack-utils/blob/main/CHANGELOG.md) | Changes in each release |

## License

[MIT](https://github.com/Neluxx/beet-datapack-utils/blob/main/LICENSE)
