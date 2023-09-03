from typing import Optional
from dataclasses import dataclass
from functools import lru_cache
from configparser import ConfigParser
import os
import shutil

import platformdirs

from mcrender.exceptions import ConfigAccessError


SCRIPT_DIR           = os.path.dirname(os.path.realpath(__file__))
DEFAULT_CONFIG_PATH  = f"{SCRIPT_DIR}/_data/default-config.conf"
CONFIG_PATH          = os.path.join(platformdirs.user_config_dir("mcrender", ensure_exists=True), "config.conf")


@dataclass
class Config:
    mineways_cmd: Optional[str] = "mineways"
    blender_cmd:  Optional[str] = "blender"


@lru_cache(maxsize=None)
def read_config_file():
    """Reads and parses the config file."""

    if not os.path.isfile(CONFIG_PATH):
        try:
            shutil.copy2(DEFAULT_CONFIG_PATH, CONFIG_PATH)
        except OSError as e:
            raise ConfigAccessError(f"Cannot write to config file {CONFIG_PATH}") from e

    parser = ConfigParser()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as file:
            parser.read_string("[DEFAULT]\n" + file.read())
    except OSError as e:
        raise ConfigAccessError(f"Cannot read config file {CONFIG_PATH}") from e

    return Config(
        mineways_cmd = parser.get("DEFAULT", "mineways-cmd", fallback=None),
        blender_cmd  = parser.get("DEFAULT", "blender-cmd",  fallback=None),
    )
