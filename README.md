# mcrender

Command-line tool and Python library for creating isometric Minecraft renders.

mcrender is a wrapper around [Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/) and [Blender](https://www.blender.org/), which do the bulk of the work. It automates the communication between these two tools, and offers a command-line/Python interface for them.

Jump to: [Installation](#installation) | [Usage - CLI](#usage---cli) | [Usage - Python](#usage---python) | [Alternatives](#alternatives) | [Acknowledgements](#acknowledgements)


# Installation

mcrender requires Python 3.7+.
It is available on PyPI, and can be installed with `pip`:
```
python3 -m pip install mcrender
```

mcrender depends on [Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/) and [Blender](https://www.blender.org/), which need to be installed manually. Mineways is Windows-only, so if you're not on Windows, you will also need [Wine](https://www.winehq.org/).

mcrender has been tested with Mineways 11.0 and Blender 3.6.2, but is expected to work with any previous or future versions with similar APIs. Blender versions before 2.8 are not supported.

In addition, mcrender needs to know how it can access these dependencies: you need to specify commands that will run Mineways and Blender on your system.
It is possible to specify these commands every time you call mcrender, but it is recommended to set default commands in mcrender's config file.

The location of the config file depends on your operating system. It is shown at the bottom of the `mcrender --help` message.
If the config file doesn't exist, mcrender creates a default one when you run it.

The config file has two keys:
- `mineways-cmd`: Command to run Mineways.\
  Set this to a command that will run Mineways on your system. If you run Mineways through Wine, an example command would be `wine /path/to/Mineways.exe`

- `blender-cmd`: Command to run Blender.\
  Set this to a command that will run Blender on your system. The default value `blender` is probably fine.


# Usage - CLI

To run mcrender, use:

```
mcrender [options] <world path> <output path>
```

You also need to specify which 3D box of the Minecraft world to render. This can be done in two ways:
1. Using `--pos` and `--size`.
2. Using two `--pos` options: one for each corner (inclusive).

Options:
| Option                   | Description                                                   | Default  |
|--------------------------|---------------------------------------------------------------|----------|
| `-p, --pos  <x> <y> <z>` | Render-box corner                                             |          |
| `-s, --size <x> <y> <z>` | Render-box size                                               |          |
| `--rotation {0,1,2,3}`   | Rotation of the camera.                                       | 0        |
| `--exposure <float>`     | Post-processing exposure (brightness). Can be negative.       | 0        |
| `--trim / --no-trim`     | Whether to trim the output image.*                            | `--trim` |
| `-f, --force`            | Overwrite any existing file at the output path.               |          |
| `--mineways-cmd <cmd>`   | Command to run Mineways. Overrides the config file's command. |          |
| `--blender-cmd <cmd>`    | Command to run Blender. Overrides the config file's command.  |          |
| `-v, --verbose`          | Print more information.                                       |          |
| `-q, --quiet`            | Cancel a previous --verbose.                                  |          |
| `--version`              | Show the version and exit.                                    |          |
| `--help`                 | Show a help message and exit.                                 |          |

*: The render is always created at a resolution of 2048x2048 pixels, but the model may not be square. If `--trim` is set (which it is by default), the image is trimmed down to the model's bounding box. Otherwise, the model will be centered in the image.

Example usage:
```
mcrender -v /path/to/minecraft-world -p 0 60 0 -s 64 128 64 --rotation 1 snippet.png
```


# Usage - Python

TODO


# Alternatives

Rendering Minecraft worlds is not a new concept. This particular tool is mainly intended for use in scripts or larger systems. It's very automatable, but not very interactive.

Advantages of mcrender compared to other rendering tools:
- Easily automatable
- No need to open Minecraft, modify it, or even install it

Disadvantages:
- Not very interactive; cannot select region in-game.
- Depends on Mineways and Blender, which must be installed separately.

 Here are a few alternatives for different use cases that I came across. Disclaimer: I have not tried most of them, so these descriptions may be inaccurate.

- [Chunky](https://chunky-dev.github.io/docs/)\
  Very extensive GUI rendering system for Minecraft. Can do more than just isometric renders.

- [Isometric Renders mod](https://www.curseforge.com/minecraft/mc-mods/isometric-renders)\
  A mod that allows you to render world snippets or items in-game.

- [mcmap](https://github.com/spoutn1k/mcmap)\
  Creates pixel art renders instead of using Minecraft textures. Has an out-of-game command-line interface similar to mcrender.

- [CyclesMineways](https://github.com/JMY1000/CyclesMineways/)\
  Blender script for rendering Mineways output with Blender's cycles renderer. Compared to mcrender, does not automate the Mineways part and requires an old version of Blender (<2.80), but uses a more sophisticated renderer.

- [A script from World-GAN](https://github.com/Mawiszus/World-GAN/blob/main/minecraft/level_renderer.py)\
  The main inspiration for mcrender. Automates only the Mineways part, but the repository also contains a modified version of CyclesMineways for the Blender part. No command-line interface. Note that the script somewhat confusingly refers to Mineways object creation as "rendering".

- Manual [Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/) with a rendering engine (like [Blender](https://www.blender.org/)'s)\
  Mineways creates models of Minecraft world snippets, which can be 3D printed or rendered. Using Mineways and a rending engine separately is more complex, but opens up more possibilities.


# Acknowledgements

mcrender was inspired by the scripts from [World-GAN](https://github.com/Mawiszus/World-GAN), as described under [Alternatives](#alternatives).

Blender files were created by [Björn van der scheer](https://bluespike.artstation.com/).
