"""Helpers for building Minecraft datapacks for several versions with beet.

`versioned_packs(ctx)` returns the base pack and every overlay, each with its
Minecraft version. `VersionedPack.edit` edits a file of that version.
"""

from .fields import first_existing_key, get_config, set_range
from .file_types import CARVER, FEATURE
from .packs import VersionedPack, versioned_packs

__all__ = [
    "CARVER",
    "FEATURE",
    "VersionedPack",
    "first_existing_key",
    "get_config",
    "set_range",
    "versioned_packs",
]
