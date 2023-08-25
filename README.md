# mcrender

Command-line tool and Python library for creating isometric Minecraft renders.

`mcrender` is a wrapper around [Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/) and [Blender](https://www.blender.org/), which do the bulk of the work. It automates the communication between these two tools, and offers a command-line/Python interface for them. Mineways and Blender need to be installed manually.

`mcrender` has been tested with Mineways 11.0 and Blender 3.6.2.

# Alternatives

Rendering Minecraft worlds is not a new concept. This particular tool is mainly intended for use in scripts or larger systems. It's very automatable, but not very interactive.

Advantages of `mcrender` compared to other rendering tools:
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
  Creates pixel art renders instead of using Minecraft textures. Has an out-of-game command-line interface similar to `mcrender`.

- [CyclesMineways](https://github.com/JMY1000/CyclesMineways/)\
  Blender script for rendering Mineways output with Blender's cycles renderer. Compared to `mcrender`, does not automate the Mineways part and requires an old version of Blender (<2.80), but uses a more sophisticated renderer.

- [A script from World-GAN](https://github.com/Mawiszus/World-GAN/blob/main/minecraft/level_renderer.py)\
  The main inspiration for `mcrender`. Automates only the Mineways part, but the repository also contains a modified version of CyclesMineways for the Blender part. No command-line interface. Note that the script somewhat confusingly refers to Mineways object creation as "rendering".

- Manual [Mineways](https://www.realtimerendering.com/erich/minecraft/public/mineways/) with a rendering engine (like [Blender](https://www.blender.org/)'s)\
  Mineways creates models of Minecraft world snippets, which can be 3D printed or rendered. Using Mineways and a rending engine separately is more complex, but opens up more possibilities.


# Acknowledgements

`mcrender` was inspired by the scripts from [World-GAN](https://github.com/Mawiszus/World-GAN), as described under **Alternatives**.

Blender files were created by [Björn van der scheer](https://bluespike.artstation.com/).
