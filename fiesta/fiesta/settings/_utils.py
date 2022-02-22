from pathlib import Path

from configurations.values import CastingMixin, Value


class PathValue(CastingMixin, Value):
    caster = Path


class BaseConfigurationProtocol:
    DEBUG: bool
    BASE_DIR: Path
