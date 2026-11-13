# Installation

## Requirements

- [Python](https://www.python.org/) 3.14+
- [beet](https://github.com/mcbeet/beet) 0.119.0+
- A package manager such as [uv](https://docs.astral.sh/uv/)

## Adding the package to your datapack

Add the package to the dependencies of your datapack:

```bash
uv add beet-datapack-utils
```

With pip:

```bash
pip install beet-datapack-utils
```

Or add it to the `pyproject.toml` of your datapack yourself and run `uv lock`:

```toml
[project]
dependencies = [
    "beet>=0.119.0",
    "beet-datapack-utils>=0.1.0",
]
```

## Building

Build your datapack with:

```bash
uv run beet build
```

Do not use `uvx beet`: it runs beet in an isolated environment without your dependencies, so the import of `beet_datapack_utils` fails.

The first build that reads vanilla files downloads the needed Minecraft versions. Packs that only write their own files build offline.

## Updating

```bash
uv lock --upgrade-package beet-datapack-utils
```

See the [changelog](../CHANGELOG.md) for what changed. Major versions may rename or remove public functions.

## Next steps

- [Usage](USAGE.md): configure `beet.yml` for your versions.
- [API reference](API.md): all public classes and functions.
- To try an unreleased version from a local checkout, see [Development](DEVELOPMENT.md#trying-changes-in-a-datapack).
