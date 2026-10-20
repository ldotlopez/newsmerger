"""Plugin bundles. Each module is loaded only when `plugins:` in the config
has a section with its name, and exposes `__newsmerger_plugin__(**options)`,
which validates that section and returns the objects the bundle provides.
"""

from typing import Any

import pydantic

# What an entry point returns: (object name, Protocol, object) per object.
type PluginObjects = list[tuple[str, type, Any]]


class PluginOptions(pydantic.BaseModel):
    """Base for a plugin's options: unknown keys are errors."""

    model_config = pydantic.ConfigDict(extra="forbid")
