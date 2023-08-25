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
__version__          = "0.1.0"


# ==================================================================================================


import subprocess
from tempfile import TemporaryDirectory
import os
import sys

from PIL import Image


SCRIPT_DIR          = os.path.dirname(os.path.realpath(__file__))
BLENDER_BLEND_PATH  = f"{SCRIPT_DIR}/_data/blender/mineways-isometric.blend"
BLENDER_SCRIPT_PATH = f"{SCRIPT_DIR}/_data/blender/mineways-isometric.py.txt"


# --------------------------------------------------------------------------------------------------
# Mineways

# Inspired by https://github.com/Mawiszus/World-GAN/blob/main/minecraft/level_renderer.py
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
    mineways_cmd:    str = "mineways"
 ):
    if size_x <= 0 or size_y <= 0 or size_z <= 0:
        raise ValueError("The size must be positive in each dimension.")

    with TemporaryDirectory() as tmpDir:
        scriptPath = tmpDir + "/script.mwscript"

        with open(scriptPath, "w", encoding="utf-8") as f:
            # https://www.realtimerendering.com/erich/minecraft/public/mineways/scripting.html
            f.write(f"Save Log file: {tmpDir}/log.txt\n")
            f.write("Show informational: false\n")
            f.write("Show warning: false\n")
            f.write("Show error: false\n")
            f.write(f"Minecraft world: {world_path}\n")
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

        cmd = [mineways_cmd, "-m", "-s", "none", scriptPath]
        subprocess.run(cmd, universal_newlines=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


# --------------------------------------------------------------------------------------------------
# Blender


def blender_render_obj(
    output_path: str,
    obj_path:    str,
    exposure:    float = 0,
    trim:        bool  = False,
    blender_cmd: str   = "blender"
):
    with TemporaryDirectory() as tmpDir:
        cmd  = [blender_cmd, "--background", BLENDER_BLEND_PATH, "--python", BLENDER_SCRIPT_PATH, "--", "--exposure", str(exposure), obj_path, f"{tmpDir}/output"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

        if trim:
            with Image.open(f"{tmpDir}/output0001.png") as image:
                trimmed = image.crop(image.getbbox())
            trimmed.save(f"{tmpDir}/output0001.png")

        if os.path.dirname(output_path): os.makedirs(os.path.dirname(output_path), exist_ok=True)
        os.rename(f"{tmpDir}/output0001.png", output_path)


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
    exposure:     float = 0,
    trim:         bool  = False,
    mineways_cmd: str   = "mineways",
    blender_cmd:  str   = "blender",
    verbose:      bool  = False,
):
    with TemporaryDirectory() as tmpDir:
        if verbose: print("Running Mineways...", file=sys.stderr)
        mineways_make_obj(tmpDir, "snippet", world_path, x, y, z, size_x, size_y, size_z, rotation, mineways_cmd)
        if verbose: print("Rendering...", file=sys.stderr)
        blender_render_obj(output_path, f"{tmpDir}/snippet.obj", exposure, trim, blender_cmd)
        if verbose: print(f"Created {output_path}", file=sys.stderr)
