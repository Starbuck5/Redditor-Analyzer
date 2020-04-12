import os
from pgx.data import data

# localizes filepaths so that file loading works for whatever the local os is
# paths can be mac formatted (dir/file) or pc formatted (dir\\file)
"""
right now only supports relative paths, but could test for absolute paths and support those too
https://docs.python.org/3/library/os.path.html#os.path.isabs
"""


def handle_path(path, internal=False):
    if "\\" in path and "/" in path:
        raise ValueError(
            "path should be either windows formatted (dir\\file), or unix formatted (dir/file), not both"
        )

    if "\\" in path:
        path = path.split("\\")
    elif "/" in path:
        path = path.split("/")
    else:  # ex: a path without any directories
        path = [path]

    basepath = data.get_internalpath() if internal else data.get_projectpath()

    return os.path.join(basepath, *path)
