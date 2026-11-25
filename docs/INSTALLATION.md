# Installation

## Requirements

- [Python](https://www.python.org/) 3.14 or newer
- [beet](https://github.com/mcbeet/beet) 0.121.2 or newer (installed automatically as a dependency)
- A package manager. [uv](https://docs.astral.sh/uv/) is recommended.

## Install

Run this in your datapack project:

```bash
uv add beet-datapack-utils
```

If you use pip instead:

```bash
pip install beet-datapack-utils
```

You can also add the package to your `pyproject.toml` yourself and then run `uv lock`:

```toml
[project]
dependencies = [
    "beet>=0.121.2",
    "beet-datapack-utils>=1.0.0",
]
```

## Build

```bash
uv run beet build
```

Use `uv run beet`, not `uvx beet`. `uvx` runs beet in an isolated environment without your project's dependencies, so importing `beet_datapack_utils` fails.

The first build that reads vanilla files downloads the Minecraft versions it needs. Packs that only write their own files build offline.

## Update

```bash
uv lock --upgrade-package beet-datapack-utils
```

Check the [changelog](../CHANGELOG.md) before updating. A new major version may rename or remove public functions.
