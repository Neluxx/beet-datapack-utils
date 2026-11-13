# Usage

## Configuring `beet.yml`

Declare the Minecraft version of the base pack in `meta.base_version`, and the version of each overlay in `meta.overlay_versions` (overlay directory → version):

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

- Every key of `overlay_versions` should be the `directory` of an overlay in `data_pack.overlays`. A directory that is not configured there is created with beet's default pack format.
- The library does not set pack formats. Configure them in `data_pack` as usual in beet. If you leave them out, beet uses the format of the latest Minecraft version it knows.
- The base pack is built from the vanilla files of `base_version`, but every version in its format range that no overlay covers loads it. So use the oldest version you support as `base_version`, and add an overlay for each version that changed a file you patch.
- Only release versions such as `1.21.9` or `26.3` are supported, not snapshots or pre-releases (`25w45a`, `1.21.9-pre1`).

`src.plugins.canyon` is the module `src/plugins/canyon.py` in your project, with a `beet_default(ctx)` function like the one in the [README](../README.md).

## Next steps

See the [API reference](API.md) for all helpers.
