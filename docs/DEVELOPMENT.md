# Development

## Requirements

- [Python](https://www.python.org/) 3.14 or newer
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/Neluxx/beet-datapack-utils.git
cd beet-datapack-utils
uv sync
```

`uv sync` creates the virtual environment and installs the package together with its development dependencies.

## Tests and code style

```bash
uv run pytest          # tests, including doctests in src/
uv run ruff check      # linting
uv run ruff format     # formatting
```

The tests replace beet's `Vanilla` service with a small in-memory fake (see `tests/conftest.py`), so they run offline and never download Minecraft.

CI runs `ruff format --check`, `ruff check`, `pytest` and `uv build` on every pull request and on every push to `main`.

## Testing changes in a datapack

To try unreleased changes, point your datapack's `pyproject.toml` to your local checkout:

```toml
[tool.uv.sources]
beet-datapack-utils = { path = "../beet-datapack-utils", editable = true }
```

Then run `uv sync` and `uv run beet build` in the datapack. Remove the entry again before you commit.

## Project structure

```
.
├── docs/                  # Documentation
├── src/beet_datapack_utils/
│   ├── __init__.py        # Public API
│   ├── target.py          # targets() and Target
│   ├── file_types.py      # CARVER, FEATURE, Moved
│   ├── fields.py          # Fields that changed between versions
│   └── density.py         # Density function helpers
├── tests/
├── CHANGELOG.md
└── pyproject.toml
```

When you add a public helper, export it in `__init__.py` (including `__all__`) and add it to the helper tables in [USAGE.md](USAGE.md). Only add helpers that a real datapack needs.

## Conventions

- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org/): `<type>: <short description>`. Common types are `feat`, `fix`, `docs`, `refactor`, `chore`, `build` and `style`.
- **Changelog:** add every user-facing change to the `Unreleased` section of [CHANGELOG.md](../CHANGELOG.md).
- **Versioning** follows [Semantic Versioning](https://semver.org/). Renaming or removing a public function requires a major version bump.

## Releasing

1. Update `version` in `pyproject.toml` and move the `Unreleased` entries in `CHANGELOG.md` to a new version section.
2. Commit, tag and push:
   ```bash
   git tag v1.1.0
   git push origin v1.1.0
   ```
3. The release workflow checks that the tag matches the package version, runs the tests, builds the package and publishes it to [TestPyPI](https://test.pypi.org/project/beet-datapack-utils/).
4. Check the TestPyPI release, then approve the `pypi` deployment in the workflow run. The same files are then published to [PyPI](https://pypi.org/project/beet-datapack-utils/) and attached to a new GitHub release.
5. In each datapack, run `uv lock --upgrade-package beet-datapack-utils`.
