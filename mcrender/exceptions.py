"""Exception classes used by mcrender"""


class ConfigAccessError(RuntimeError):
    """Raised when the config file cannot be accessed."""


class CommandNotSetError(RuntimeError):
    """Raised when a dependency command is not set."""


class MinewaysCommandNotSetError(CommandNotSetError):
    """Raised when the Mineways command is not set."""


class BlenderCommandNotSetError(CommandNotSetError):
    """Raised when the Blender command is not set."""
