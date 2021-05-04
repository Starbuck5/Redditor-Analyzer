import pygame

# General utilities
from pgx.path import path

path._init()  # init pathing asap

from pgx.events import events
from pgx.time import time
from pgx.key import key
from pgx.File import File
from pgx.Rect import Rect
import pgx.image

# Rarely used, but hopefully useful utilities
from pgx.compiler import compiler

# UI system
from pgx.scale import scale
import pgx.ui
from pgx.font import font
from pgx.Text import Text
from pgx.Text import LinedText
from pgx.Location import Location

# Experimental
from pgx.handle_error import handle_error


class version:
    vernum = (0, 8, 0)
    ver = "0.8"


__version__ = version.ver


def init(resolution) -> None:
    scale.set_resolution(resolution)

    pygame.mixer.init()

    font._init()
    Text._init()

    pygame.key.set_repeat(500, 20)


def tick(*args) -> None:
    # fps limiter - optional
    time._tick(*args)

    # gets the event stuff updated
    events._update()

    # gets the keyboard ready to respond
    key._prepare()
