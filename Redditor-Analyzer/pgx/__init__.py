import pygame
import os
import sys

# Internals, should probably be consolidated into this file
from pgx.data import data
from pgx.handle_path import handle_path

# from pgx.interpret_coords import interpret_coords

# General Utilities
from pgx.events import events
from pgx.time import time
from pgx.key import key
from pgx.File import File
from pgx.image import image

# Rarely used, but hopefully useful utilities
from pgx.compiler import compiler

# UI system
import pgx.ui
from pgx.font import font
from pgx.Text import Text
from pgx.Location import Location


def init(resolution):
    data._resolution = list(resolution)

    """
    with pygame 2 use this instead of an arg into init
    data._resolution = pygame.display.get_window_size()
    """

    pygame.mixer.init()  # not yet used b/c click sound effect hasn't been implemented

    if getattr(sys, "frozen", False):
        data._internalpath = os.path.dirname(os.path.abspath(__file__))
        data._projectpath = os.path.dirname(sys.executable)

    else:
        data._internalpath = os.path.dirname(os.path.abspath(__file__))
        data._projectpath = os.getcwd()

    font.init()

    Text.init()

    pygame.key.set_repeat(500, 20)


def tick(*args):
    # fps limiter - optional
    # clock.tick(*args)
    time._tick(*args)

    # gets the event stuff updated
    events._update()

    # gets the keyboard ready to respond
    key._prepare()

    # for event in events.get():
    #    if event.type == pygame.VIDEORESIZE:
    #        _adjust_scalings(get_scaling_mode())


scaling_modes = ["none", "center", "full", "manual"]


def set_scaling_mode(mode="manual"):
    if mode in scaling_modes:
        if mode != get_scaling_mode():
            data._scaling_mode = mode
            apply_scaling()
    else:
        raise ValueError(
            f"Not a valid scaling mode, these are the options: {scaling_modes}"
        )


def get_scaling_mode():
    return data._scaling_mode


def apply_scaling():
    mode = get_scaling_mode()
    screen_size = pygame.display.get_surface().get_size()
    native_res = data.get_resolution()

    if mode == "manual":
        return

    if mode == "none":
        scale = 1
        adjustments = [0, 0]

    elif mode == "center":
        scale = 1
        adjustments = [(screen_size[i] - native_res[i]) / 2 for i in range(2)]

    elif mode == "full":
        screen_size = pygame.display.get_surface().get_size()
        native_res = data.get_resolution()

        xandy = [screen_size[i] / native_res[i] for i in range(2)]
        scale = min(xandy)

        xandy = [num / scale for num in xandy]
        adjustments = [(xandy[i] - 1) / 2 * screen_size[i] / xandy[i] for i in range(2)]

    data.set_global_scale(scale)
    data.set_global_offset(adjustments)
