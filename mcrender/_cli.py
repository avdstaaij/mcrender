from typing import Optional, Tuple

from click import UsageError
import cloup

from mcrender import render


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
@cloup.option("--exposure",       metavar="<float>",      help="Exposure for post-processing.", type=float, default=0)
@cloup.option("--trim/--no-trim",                         help="Trim the output image.",                 default=False)
@cloup.option("--mineways-cmd",   metavar="<cmd>",        help="Command to run Mineways.",               type=str, default="mineways")
@cloup.option("--blender-cmd",    metavar="<cmd>",        help="Command to run Blender.",                type=str, default="blender")
def cli(world_path: str, pos: Tuple[Tuple[int]], size: Optional[Tuple[int]], output_path: str, rotation: int, exposure: float, trim: bool, mineways_cmd: str, blender_cmd: str):
    """
    Render a Minecraft world snippet with Mineways and Blender.

    \b
    You can specify the box to render in two ways:
    1. Using --pos and --size.
    2. Using two --pos options: one for each corner (inclusive).
    """

    def raise_box_spec_error():
        raise UsageError("You must either set --pos and --size, or set --pos twice.")

    if len(pos) == 1:
        if size is None:
            raise_box_spec_error()
        offset = pos[0]

    elif len(pos) == 2:
        if size is not None:
            raise_box_spec_error()

        x1, x2 = sorted((pos[0][0], pos[1][0]))
        y1, y2 = sorted((pos[0][1], pos[1][1]))
        z1, z2 = sorted((pos[0][2], pos[1][2]))

        offset = (x1, y1, z1)
        size = (x2 - x1 + 1, y2 - y1 + 1, z2 - z1 + 1)

    else:
        raise_box_spec_error()

    render(
        output_path  = output_path,
        world_path   = world_path,
        x            = offset[0],
        y            = offset[1],
        z            = offset[2],
        size_x       = size[0],
        size_y       = size[1],
        size_z       = size[2],
        rotation     = rotation,
        exposure     = exposure,
        trim         = trim,
        mineways_cmd = mineways_cmd,
        blender_cmd  = blender_cmd
    )
