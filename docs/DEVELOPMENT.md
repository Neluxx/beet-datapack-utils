# Development

## Requirements

- [Python](https://www.python.org/) 3.14+
- [uv](https://docs.astral.sh/uv/) (package manager)

## Setup

Create the virtual environment and install the package with its development dependencies:

```powershell
uv sync
```

## Tests and linting

```powershell
# Run the tests (including the doctests in the source)
uv run pytest

# Check code style and imports
uv run ruff check

# Format the code
uv run ruff format
```

The tests replace beet's `Vanilla` service with a small in-memory fake (see `tests/conftest.py`), so they run offline and do not download Minecraft.

## Trying changes in a datapack

To test unreleased changes, point the datapack to your local checkout instead of the Git tag:

```toml
[tool.uv.sources]
beet-datapack-utils = { path = "../beet-datapack-utils", editable = true }
```

Run `uv sync` in the datapack and build it with `uv run beet build`. Switch back to the tag before committing.

## Project Structure

```
.
├── docs/
├── src/datapack_utils/
│   ├── __init__.py        # Public API
│   ├── targets.py         # Targets service and Target.patch
│   ├── registries.py      # CARVER, FEATURE and VersionedRegistry
│   ├── fields.py          # Fields that changed between versions
│   ├── trees.py           # find_nodes and replace_nodes
│   ├── density.py         # Density function helpers
│   └── versions.py        # Version parsing and comparison
├── tests/
└── pyproject.toml         # Python project & dependency config
```

## Releasing

1. Update the version in `pyproject.toml` and move the `Unreleased` entries in `CHANGELOG.md` to a new version.
2. Commit, then tag the commit, e.g. `git tag v1.1.0`, and push the tag.
3. The release workflow checks that the tag matches the version, runs the tests and creates the GitHub release.
4. In each datapack, update the `tag` in `[tool.uv.sources]` and run `uv lock`.

Follow [Semantic Versioning](https://semver.org/): renaming or removing a public function is a major version bump.
