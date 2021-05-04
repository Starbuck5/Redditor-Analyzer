import os
import sys
import re

# localizes filepaths so that file loading works for whatever the local os is
# paths can be mac formatted (dir/file) or pc formatted (dir\\file)
# if an absolute path is entered it is just returned as is


class path:
    _internalpath = ""
    _projectpath = ""

    @staticmethod
    def _init():
        if getattr(sys, "frozen", False):
            path._internalpath = os.path.dirname(os.path.abspath(__file__))
            path._projectpath = os.path.dirname(sys.executable)

        else:
            path._internalpath = os.path.dirname(os.path.abspath(__file__))
            path._projectpath = os.getcwd()

    @staticmethod
    def handle(filepath: str, internal: bool = False) -> str:
        """Standardizes filepaths to prevent platform issues."""
        if os.path.isabs(filepath):
            return filepath

        filepath = re.split("[(\\\\)|(/)]", filepath)
        basepath = path._internalpath if internal else path._projectpath

        return os.path.join(basepath, *filepath)

    @staticmethod
    def get_internalpath() -> str:
        """Returns the absolute path to pgx's assets."""
        return path._internalpath

    @staticmethod
    def get_projectpath() -> str:
        """Returns the absolute path to the project root."""
        return path._projectpath

    @staticmethod
    def set_projectpath(filepath: str) -> None:
        """Change the project's basepath if the automatic one isn't working for you."""
        path._projectpath = filepath
