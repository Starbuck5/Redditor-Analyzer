import traceback
import platform
from datetime import datetime

import pygame

from pgx import path

# Thanks https://stackoverflow.com/a/58045927/13816541
def _get_full_class_name(obj):
    module = obj.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return obj.__class__.__name__
    return module + "." + obj.__class__.__name__


def handle_error(
    error: Exception,
    popup: bool = False,
    msg: str = "Oh no!",
    program_name: str = "The program",
) -> None:
    """Premade error logging system for crashes."""
    try:
        pygame.quit()
    except:
        pass

    with open(path.handle("errors.log"), "a+") as file:
        try:
            file.write(f"Error at {datetime.now()}\n")
        except:
            file.write("Error at undetermined time\n")

        try:
            sdl_ver = ".".join([str(v) for v in pygame.get_sdl_version()])
            os = f"{platform.system()} {platform.version()}"
            file.write(
                f"System Info: OS- {os}, SDL- {sdl_ver}, CPU- {platform.processor()}\n"
            )
        except:
            file.write("Error in getting system information\n")

        error_trace = traceback.format_tb(error.__traceback__) + [
            f"{_get_full_class_name(error)}: " + str(error) + "\n"
        ]
        for line in error_trace:
            file.write(line)

        file.write("\n")  # spacing for next error

    if popup:
        try:
            if pygame.version.vernum[0] == 2:
                from pygame._sdl2 import messagebox

                messagebox(
                    msg,
                    f"{program_name} has crashed. An error log has generated at {path.handle('errors.log')}",
                    error=True,
                )
        except:
            pass

    raise error
