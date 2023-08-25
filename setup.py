import os
from setuptools import setup


SCRIPT_DIR         = os.path.abspath(os.path.dirname(__file__))
METADATA_FILE_PATH = os.path.join(SCRIPT_DIR, "mcrender/__init__.py")


# Based on https://github.com/pypa/pip/blob/9aa422da16e11b8e56d3597f34551f983ba9fbfd/setup.py
with open(METADATA_FILE_PATH) as file:
    metadata_file_lines = file.read().splitlines()

def get_metadata(name: str) -> str:
    for line in metadata_file_lines:
        dunderString = f"__{name}__"
        if line.startswith(f"{dunderString}"):
            # __{name}__ = "{value}"
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError(f"Unable to find {dunderString} value.")


with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()


setup(
    name                          = get_metadata("title"),
    version                       = get_metadata("version"),
    description                   = get_metadata("description"),
    long_description              = long_description,
    long_description_content_type = "text/markdown",
    url                           = get_metadata("url"),
    author                        = get_metadata("author"),
    author_email                  = get_metadata("author_email"),
    license                       = get_metadata("license"),
    # classifiers=[
    # ],
    # keywords="",
    project_urls={
        "Bug Reports": "https://github.com/avdstaaij/mcrender/issues",
        "Source":      "https://github.com/avdstaaij/mcrender",
    },
    packages = ["mcrender"], # Note: subpackages must be listed explicitly
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "mcrender = mcrender._cli:cli",
        ],
    },
    python_requires=">=3.7, <4",
    install_requires=[
        "cloup >= 3.0.0",
        "Pillow"
    ],
    zip_safe=False
)