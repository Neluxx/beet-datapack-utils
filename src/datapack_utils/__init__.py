"""Helper functions for Minecraft datapacks using beet.

A datapack build has a base pack and overlays, each for a Minecraft version
(`meta.base_version` and `meta.overlay_versions` in the beet config). These
helpers copy the matching vanilla files, hide format differences between
versions and write the patched files back.
"""

__all__: list[str] = []
