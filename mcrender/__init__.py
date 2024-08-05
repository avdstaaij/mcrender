"""
Command-line tool and Python library for creating isometric Minecraft renders
with Mineways and Blender.
"""

__title__            = "mcrender"
__description__      = "Command-line tool and Python library for creating isometric Minecraft renders with Mineways and Blender."
__url__              = "https://github.com/avdstaaij/mcrender"
__author__           = "Arthur van der Staaij"
__author_email__     = "arthurvanderstaaij@gmail.com"
__license__          = "GPL-3.0-or-later"
__copyright__        = "Copyright (c) 2023 Arthur van der Staaij"
__version__          = "2.0.0"


# ==================================================================================================


from typing import Optional
from dataclasses import dataclass
from functools import lru_cache
import time
import subprocess
import os
import shutil
from tempfile import TemporaryDirectory
from configparser import ConfigParser

import platformdirs
from PIL import Image

from mcrender._util import eprint, move


_SCRIPT_DIR          = os.path.dirname(os.path.realpath(__file__))
_BLENDER_BLEND_PATH  = f"{_SCRIPT_DIR}/_data/blender/mineways-isometric.blend"
_BLENDER_SCRIPT_PATH = f"{_SCRIPT_DIR}/_data/blender/mineways-isometric.py.txt"
_DEFAULT_CONFIG_PATH = f"{_SCRIPT_DIR}/_data/default-config.conf"
CONFIG_PATH          = os.path.join(platformdirs.user_config_dir("mcrender", ensure_exists=True), "config.conf")

_DIMENSION_ID_TO_MINEWAYS_NAME = {
    "overworld":  "Overworld",
    "the_nether": "Nether",
    "nether":     "Nether",
    "the_end":    "The End",
    "end":        "The End"
}
DIMENSIONS = list(_DIMENSION_ID_TO_MINEWAYS_NAME.keys())


# --------------------------------------------------------------------------------------------------
# Exception classes


class MCRenderError(Exception):
    """Base class for all mcrender exceptions."""


class ConfigAccessError(MCRenderError):
    """Raised when the config file cannot be accessed."""


class MinewaysCommandNotSetError(MCRenderError):
    """Raised when the Mineways command is not set."""


class MinewaysLaunchError(MCRenderError):
    """Raised when the Mineways command cannot be launched."""


class MinewaysError(MCRenderError):
    """Raised when Mineways returns an error."""


class MinewaysBadWorldError(MCRenderError):
    """Raised when Mineways cannot load the world."""


class BlenderCommandNotSetError(MCRenderError):
    """Raised when the Blender command is not set."""


class BlenderLaunchError(MCRenderError):
    """Raised when the Blender command cannot be launched."""


class BlenderError(MCRenderError):
    """Raised when Blender returns an error."""


class OutputFileExistsError(MCRenderError):
    """Raised when an output file or directory already exists and cannot be overwritten."""


# --------------------------------------------------------------------------------------------------
# Config file


@dataclass
class _Config:
    mineways_cmd: Optional[str] = "mineways"
    blender_cmd:  Optional[str] = "blender"


def ensure_config_file():
    """Creates a default config file if it doesn't exist.

    Raises a ConfigAccessError if creation fails.
    """

    if not os.path.isfile(CONFIG_PATH):
        try:
            shutil.copy2(_DEFAULT_CONFIG_PATH, CONFIG_PATH)
        except OSError as e:
            raise ConfigAccessError(f"Could not create default config file at {CONFIG_PATH}") from e


@lru_cache(maxsize=None)
def _read_config_file():
    """Reads and parses the config file.

    If the config file doesn't exist, creates the default one.

    Raises a ConfigAccessError if the config file cannot be accessed.
    """

    ensure_config_file()
    parser = ConfigParser()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            parser.read_string("[DEFAULT]\n" + file.read())
    except OSError as e:
        raise ConfigAccessError(f"Could not read config file {CONFIG_PATH}") from e

    return _Config(
        mineways_cmd = parser.get("DEFAULT", "mineways-cmd", fallback=None),
        blender_cmd  = parser.get("DEFAULT", "blender-cmd",  fallback=None),
    )


# --------------------------------------------------------------------------------------------------
# Mineways


def mineways_make_obj(
    output_dir_path: str,
    output_name:     str,
    world_path:      str,
    x:               int,
    y:               int,
    z:               int,
    size_x:          int,
    size_y:          int,
    size_z:          int,
    rotation:        int = 0,
    dimension:       str = "overworld",
    mineways_cmd:    Optional[str] = None
 ):
    """Creates an OBJ model of a Minecraft world snippet using Mineways.

    The output OBJ file is written to `<output_dir_path>/<output_name>.obj`.
    Auxillary model files (like textures) are written to `<output_dir_path>`.

    Converts the snippet specified by the Minecraft world path <world_path>, the coordinate box
    <x>, <y>, <z>, <size_x>, <size_y> and <size_z>, and the dimension id <dimension>. The sizes must
    all be strictly positive. The view direction is optionally rotated by <rotation> (0, 1, 2 or 3).

    Uses <mineways_cmd> to run Mineways. If <mineways_cmd> is None, uses the command defined in the
    config file.

    Raises:
    - `ConfigAccessError` if the config file cannot be accessed.
    - `MinewaysCommandNotSetError` if the mineways command is set neither in the config file nor as
      an argument.
    - `MinewaysLaunchError` if Mineways cannot not be lauched.
    - `MinewaysError` if Mineways returns an error.
    - `MinewaysBadWorldError` if Mineways cannot load the world.

    May raise other exceptions as well, such as `OSError`.
    """

    if size_x <= 0 or size_y <= 0 or size_z <= 0:
        raise ValueError("The size must be positive in each dimension.")

    if rotation not in (0, 1, 2, 3):
        raise ValueError("The rotation must be 0, 1, 2 or 3.")

    if dimension not in DIMENSIONS:
        raise ValueError(f"The dimension must be one of {{{', '.join(DIMENSIONS)}}}.")

    if mineways_cmd is None:
        mineways_cmd = _read_config_file().mineways_cmd
        if mineways_cmd is None:
            raise MinewaysCommandNotSetError("The Mineways command is set neither in the config file nor as an argument.")

    with TemporaryDirectory() as tmpDir:
        scriptPath = f"{tmpDir}/script.mwscript"
        logPath    = f"{tmpDir}/log.txt"

        with open(scriptPath, "w", encoding="utf-8") as f:
            # https://www.realtimerendering.com/erich/minecraft/public/mineways/scripting.html
            f.write(f"Save Log file: {tmpDir}/log.txt\n")
            f.write(f"Minecraft world: {world_path}\n")
            f.write(f"View {_DIMENSION_ID_TO_MINEWAYS_NAME[dimension]}\n")
            f.write(f"Selection location min to max: {x}, {y}, {z} to {x + size_x - 1}, {y + size_y - 1}, {z + size_z - 1}\n")
            f.write("Set render type: Wavefront OBJ absolute indices\n")
            f.write("File type: Export all textures to three large images\n")
            f.write(f"Rotate model {rotation*90} degrees\n")
            f.write("Scale model by making each block 100 cm high\n")
            f.write("Tree leaves solid: yes\n")
            f.write("Use biomes: yes\n")
            f.write(f"Export for Rendering: {output_dir_path}/{output_name}.obj\n")
            f.write("Close\n")

        os.makedirs(output_dir_path, exist_ok=True)

        # If Mineways cannot find the world, it will write an error message to the log file, but it
        # won't stop. There seems to be no command-line option to make it stop in this case, either.
        # To handle this, we run Mineways in the background, periodically check the log file, and
        # kill the process if we see the error message.

        try:
            cmd = [mineways_cmd, "-m", "-suppress", "-s", "none", scriptPath]
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except OSError as e:
            raise MinewaysLaunchError(f"Mineways could not be launched: {e}") from e

        while True:
            if process.poll() is not None:
                if process.returncode != 0:
                    raise MinewaysError(f"Mineways returned an error ({process.returncode})")
                break
            try:
                with open(logPath, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("Error reading line 2: Mineways attempted to load world"):
                            process.kill()
                            raise MinewaysBadWorldError(f"Mineways could not load the world {repr(world_path)}")
            except FileNotFoundError:
                pass
            time.sleep(0.1)


# --------------------------------------------------------------------------------------------------
# Blender


def blender_render_obj(
    output_path: str,
    obj_path:    str,
    exposure:    float = 0,
    trim:        bool  = True,
    force:       bool  = False,
    blender_cmd: Optional[str] = None
):
    """Renders an OBJ file (as created by Mineways) to a PNG image using Blender.

    The output PNG file is written to <output_path>.

    The post-processing exposure can optionally be modified by <exposure> (can be negative).

    The image is created at a resolution of 2048x2048 pixels, but the model may not be square.
    If <trim> is True, the image is trimmed down to the model's bounding box.
    Otherwise, the model will be centered in the image.

    If <force> is true, overwrites any existing file at <output_path>.

    Uses <blender_cmd> to run Blender. If <blender_cmd> is None, uses the command defined in the
    config file.

    Raises:
    - `ConfigAccessError` if the config file cannot be accessed.
    - `BlenderCommandNotSetError` if the Blender command is set neither in the config file nor as an
      argument.
    - `BlenderLaunchError` if Blender cannot be launched.
    - `BlenderError` if Blender returns an error.
    - `OutputFileExistsError` if the output file already exists and <force> is false.

    May raise other exceptions as well, such as `OSError`.
    """

    if blender_cmd is None:
        blender_cmd = _read_config_file().blender_cmd
        if blender_cmd is None:
            raise BlenderCommandNotSetError("The Blender command is set neither in the config file nor as an argument.")

    with TemporaryDirectory() as tmpDir:
        try:
            cmd  = [blender_cmd, "--background", _BLENDER_BLEND_PATH, "--python", _BLENDER_SCRIPT_PATH, "--", "--exposure", str(exposure), obj_path, f"{tmpDir}/output"]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        except OSError as e:
            raise BlenderLaunchError(f"Blender could not be launched: {e}") from e
        except subprocess.CalledProcessError as e:
            raise BlenderError(f"Blender returned an error: {e}") from e

        if trim:
            with Image.open(f"{tmpDir}/output0001.png") as image:
                trimmed = image.crop(image.getbbox())
            trimmed.save(f"{tmpDir}/output0001.png")

        if os.path.dirname(output_path): os.makedirs(os.path.dirname(output_path), exist_ok=True)
        try:
            move(f"{tmpDir}/output0001.png", output_path, overwrite=force, never_overwrite_dir=True)
        except FileExistsError as e:
            raise OutputFileExistsError(str(e)) from e


# --------------------------------------------------------------------------------------------------
# Mineways + Blender


def render(
    output_path:  str,
    world_path:   str,
    x:            int,
    y:            int,
    z:            int,
    size_x:       int,
    size_y:       int,
    size_z:       int,
    rotation:     int   = 0,
    dimension:    str   = "overworld",
    exposure:     float = 0,
    trim:         bool  = True,
    force:        bool  = False,
    mineways_cmd: Optional[str] = None,
    blender_cmd:  Optional[str] = None,
    verbose:      bool  = False,
):
    """Renders a Minecraft world snippet to a PNG image using Mineways and Blender.

    The output PNG file is written to <output_path>.

    Renders the snippet specified by the Minecraft world path <world_path>, the coordinate box
    <x>, <y>, <z>, <size_x>, <size_y> and <size_z>, and the dimension id <dimension>. The sizes must
    all be strictly positive. The view direction is optionally rotated by <rotation> (0, 1, 2 or 3).

    The post-processing exposure can optionally be modified by <exposure> (can be negative).

    The image is created at a resolution of 2048x2048 pixels, but the model may not be square.
    If <trim> is True, the image is trimmed down to the model's bounding box.
    Otherwise, the model will be centered in the image.

    If <force> is true, overwrites any existing file at <output_path>.

    Uses <mineways_cmd> to run Mineways and <blender_cmd> to run Blender.
    If either argument is None, uses the command defined in the config file.

    Raises:
    - `ConfigAccessError` if the config file cannot be accessed.
    - `MinewaysCommandNotSetError` if the mineways command is set neither in the config file nor as
      an argument.
    - `MinewaysLaunchError` if Mineways cannot not be lauched.
    - `MinewaysError` if Mineways returns an error.
    - `MinewaysBadWorldError` if Mineways cannot load the world.
    - `BlenderCommandNotSetError` if the Blender command is set neither in the config file nor as an
      argument.
    - `BlenderLaunchError` if Blender cannot be launched.
    - `BlenderError` if Blender returns an error.
    - `OutputFileExistsError` if the output file already exists and <force> is false.

    May raise other exceptions as well, such as `OSError`.
    """
    with TemporaryDirectory() as tmpDir:
        if verbose: eprint("Running Mineways...")
        mineways_make_obj(tmpDir, "snippet", world_path, x, y, z, size_x, size_y, size_z, rotation, dimension, mineways_cmd)
        if verbose: eprint("Rendering...")
        blender_render_obj(output_path, f"{tmpDir}/snippet.obj", exposure, trim, force, blender_cmd)
        if verbose: eprint(f"Created {output_path}")
