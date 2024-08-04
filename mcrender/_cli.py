"""mcrender command-line interface."""

from typing import Optional, Tuple
import sys

from click import UsageError
import cloup

import mcrender
from mcrender._util import eprint


def parse_box_spec(pos: Tuple[Tuple[int]], size: Optional[Tuple[int]]) -> Tuple[int]:
    """Parses specified pos and size arguments into a (x,y,z,sx,sy,sz) tuple."""

    def raise_box_spec_error():
        raise UsageError(
            "The box to render is not specified.\n"
            "You can specify the box to render in two ways:\n"
            "1. Using --pos and --size.\n"
            "2. Using two --pos options: one for each corner (inclusive)."
        )

    if len(pos) == 1:
        if size is None:
            raise_box_spec_error()

        pos  = list(pos[0])
        size = list(size)
        for i in range(3):
            if size[i] == 0:
                raise UsageError(f"The box to render has size 0 in the {['X', 'Y', 'Z'][i]}-axis.")
            if size[i] < 0:
                pos[i] += size[i]
                size[i] = -size[i]

        return *pos, *size

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

epilog = (
    f"*: Dimension options: {{{', '.join(mcrender.DIMENSIONS)}}}\n"
    "\n"
    "**: The render is always created at a resolution of 2048x2048 pixels, but the model may not be square. If `--trim` is set (which it is by default), the image is trimmed down to the model's bounding box. Otherwise, the model will be centered in the image.\n"
    "\n"
    f"Config file location: {mcrender.CONFIG_PATH}\n"
)

# pylint: disable=no-value-for-parameter
@cloup.command(context_settings={"show_default": True}, epilog=epilog)
@cloup.argument("world-path",  metavar="<world path>",  type=cloup.Path(exists=True, file_okay=False))
@cloup.argument("output-path", metavar="<output path>", type=cloup.Path())
@cloup.option("--pos",  "-p",     metavar=" <x> <y> <z>", help="Render-box corner",                           type=int, nargs=3, multiple=True)
@cloup.option("--size", "-s",     metavar="<x> <y> <z>",  help="Render-box size",                             type=int, nargs=3)
@cloup.option("--rotation",       metavar="{0,1,2,3}",    help="Rotation of the camera.",                     type=int, default=0)
@cloup.option("--dimension",      metavar="<id>",         help="World dimension.*",                           type=str, default="overworld")
@cloup.option("--exposure",       metavar="<float>",      help="Exposure for post-processing.",               type=float, default=0)
@cloup.option("--trim/--no-trim",                         help="Trim the output image.**",                    default=True)
@cloup.option("--force", "-f",                            help="Overwrite any existing file at output path.", is_flag=True)
@cloup.option("--mineways-cmd",   metavar="<cmd>",        help="Command to run Mineways.",                    type=str)
@cloup.option("--blender-cmd",    metavar="<cmd>",        help="Command to run Blender.",                     type=str)
@cloup.option("--verbose", "-v", "verbose",               help="Print more information.",                     flag_value=True)
@cloup.option("--quiet",   "-q", "verbose",               help="Cancel a previous --verbose.",                flag_value=False, default=False, show_default=False)
@cloup.version_option(mcrender.__version__, package_name="mcrender", prog_name="mcrender", message="%(prog)s %(version)s")
def cli(world_path: str, output_path: str, pos: Tuple[Tuple[int]], size: Optional[Tuple[int]], rotation: int, dimension: str, exposure: float, trim: bool, force: bool, mineways_cmd: Optional[str], blender_cmd: Optional[str], verbose: bool):
    """
    Render a Minecraft world snippet with Mineways and Blender.

    \b
    You can specify the box to render in two ways:
    1. Using --pos and --size.
    2. Using two --pos options: one for each corner (inclusive).
    """

    error_prefix = "\nError: " if verbose else "Error: "

    box = parse_box_spec(pos, size)

    try:
        mcrender.render(
            output_path  = output_path,
            world_path   = world_path,
            x            = box[0],
            y            = box[1],
            z            = box[2],
            size_x       = box[3],
            size_y       = box[4],
            size_z       = box[5],
            rotation     = rotation,
            dimension    = dimension,
            exposure     = exposure,
            trim         = trim,
            force        = force,
            mineways_cmd = mineways_cmd,
            blender_cmd  = blender_cmd,
            verbose      = verbose
        )
        return
    except mcrender.ConfigAccessError as e:
        eprint(f"{error_prefix}{e}\n    {e.__cause__}", file=sys.stderr)
    except mcrender.MinewaysCommandNotSetError:
        eprint(f"{error_prefix}You must either set --mineways-cmd, or set mineways-cmd in\n{repr(mcrender.CONFIG_PATH)}.")
    except mcrender.BlenderCommandNotSetError:
        eprint(f"{error_prefix}You must either set --blender-cmd, or set blender-cmd in\n{repr(mcrender.CONFIG_PATH)}.")
    except mcrender.MinewaysLaunchError as e:
        eprint(f"{error_prefix}Mineways could not be launched.\n    {e.__cause__}\n")
        if mineways_cmd is not None:
            eprint(
                 "Make sure that you have downloaded Mineways and that your specified",
                f"command ({repr(mineways_cmd)}) runs it.",
                sep="\n"
            )
        else:
            eprint(
                "Make sure that you have downloaded Mineways and that your configured",
                f"mineways-cmd (in {repr(mcrender.CONFIG_PATH)}) runs it.",
                sep="\n"
            )
    except mcrender.BlenderLaunchError as e:
        eprint(f"{error_prefix}Blender could not be launched.\n    {e.__cause__}\n")
        if blender_cmd is not None:
            eprint(
                 "Make sure that you have downloaded Blender and that your specified",
                f"command ({repr(blender_cmd)}) runs it.",
                sep="\n"
            )
        else:
            eprint(
                "Make sure that you have downloaded Blender and that your configured",
                f"blender-cmd (in {repr(mcrender.CONFIG_PATH)}) runs it.",
                sep="\n"
            )
    except mcrender.MinewaysError as e:
        eprint(f"{error_prefix}{e}")
    except mcrender.MinewaysBadWorldError as e:
        eprint(
            f"{error_prefix}Mineways could not load the specified world",
            f"{repr(world_path)}.",
            "",
            "There might still be a Mineways window open that you'll have to close",
            "manually. Sorry about that, I'm afraid I don't know how to prevent it.",
            sep="\n"
        )
    except mcrender.BlenderError as e:
        eprint(f"{error_prefix}Blender returned an error.\n    {e.__cause__}")
    except mcrender.OutputFileExistsError as e:
        eprint(f"{error_prefix}{e}")

    sys.exit(1)


def main():
    try:
        mcrender.ensure_config_file()
    except mcrender.ConfigAccessError as e:
        eprint(f"Warning: {e}\n    {e.__cause__}\n")
        eprint("If this execution requires the config file, it will fail.\n")

    cli()
