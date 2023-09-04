from typing import Optional, Tuple
import sys

from click import UsageError
import cloup

from mcrender import render, ConfigAccessError, MinewaysCommandNotSetError, BlenderCommandNotSetError, _CONFIG_PATH


def parse_box_spec(pos: Tuple[Tuple[int]], size: Optional[Tuple[int]]) -> Tuple[int]:
    """Parses specified pos and size arguments into a (x,y,z,sx,sy,sz) tuple."""

    def raise_box_spec_error():
        raise UsageError("You must either set --pos and --size, or set --pos twice.")

    if len(pos) == 1:
        if size is None:
            raise_box_spec_error()
        return *pos[0], *size

    if len(pos) == 2:
        if size is not None:
            raise_box_spec_error()

        x1, x2 = sorted((pos[0][0], pos[1][0]))
        y1, y2 = sorted((pos[0][1], pos[1][1]))
        z1, z2 = sorted((pos[0][2], pos[1][2]))

        return x1, y1, z1, x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1

    raise_box_spec_error()


# We have to take the position as an option instead of a positional argument,
# because otherwise you need to use "--" to pass negative numbers, which is
# quite unintuitive. For consistency, we take the size as an option as well.

# pylint: disable=no-value-for-parameter
@cloup.command(context_settings={"show_default": True})
@cloup.argument("world-path",  metavar="<world path>",  type=cloup.Path())
@cloup.argument("output-path", metavar="<output path>", type=str)
@cloup.option("--pos",  "-p",     metavar=" <x> <y> <z>", help="Render-box corner",                      type=int, nargs=3, multiple=True)
@cloup.option("--size", "-s",     metavar="<x> <y> <z>",  help="Render-box size",                        type=int, nargs=3)
@cloup.option("--rotation",       metavar="{0,1,2,3}",    help="Rotation of the camera.",                type=int, default=0)
@cloup.option("--exposure",       metavar="<float>",      help="Exposure for post-processing.",          type=float, default=0)
@cloup.option("--trim/--no-trim",                         help="Trim the output image.",                 default=True)
@cloup.option("--mineways-cmd",   metavar="<cmd>",        help="Command to run Mineways.",               type=str)
@cloup.option("--blender-cmd",    metavar="<cmd>",        help="Command to run Blender.",                type=str)
@cloup.option("--verbose", "-v", "verbose",               help="Print more information.",                flag_value=True)
@cloup.option("--quiet",   "-q", "verbose",               help="Cancel a previous --verbose.",           flag_value=False, default=False, show_default=False)
def cli(world_path: str, pos: Tuple[Tuple[int]], size: Optional[Tuple[int]], output_path: str, rotation: int, exposure: float, trim: bool, mineways_cmd: Optional[str], blender_cmd: Optional[str], verbose: bool):
    """
    Render a Minecraft world snippet with Mineways and Blender.

    \b
    You can specify the box to render in two ways:
    1. Using --pos and --size.
    2. Using two --pos options: one for each corner (inclusive).
    """

    box = parse_box_spec(pos, size)

    try:
        render(
            output_path  = output_path,
            world_path   = world_path,
            x            = box[0],
            y            = box[1],
            z            = box[2],
            size_x       = box[3],
            size_y       = box[4],
            size_z       = box[5],
            rotation     = rotation,
            exposure     = exposure,
            trim         = trim,
            mineways_cmd = mineways_cmd,
            blender_cmd  = blender_cmd,
            verbose      = verbose
        )
    except ConfigAccessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except MinewaysCommandNotSetError:
        print(f"Error: You must either set --mineways-cmd, or set mineways-cmd in {_CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
    except BlenderCommandNotSetError:
        print(f"Error: You must either set --blender-cmd, or set blender-cmd in {_CONFIG_PATH}", file=sys.stderr)
        sys.exit(1)
