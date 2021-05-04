import copy

import pygame

from pgx.events import events
from pgx import image

from pgx.ui.UI import UI
from pgx.ui.shape import shape


__all__ = [
    "Panel",
    "Box",
    "ImageBox",
    "TextBox",
    "Button",
    "Drawing",
    "Row",
    "Column",
]


class Panel(UI):
    def _display(self, _):
        pass

    # public attributes
    # everything in general UI


class Box(UI):
    def __init__(self, location, color, width=0, **kwargs):
        super().__init__(location)
        self.color = color
        self.orig_width = width
        self.width = width

        self.orig_border_radius = (
            0 if "border_radius" not in kwargs else kwargs["border_radius"]
        )
        self.border_radius = self.orig_border_radius

    def _display(self, screen):
        rect = self.location.resolve()
        pygame.draw.rect(
            screen, self.color, rect, self.width, border_radius=self.border_radius
        )

    def _scale(self):
        # adjusts original width by the scale
        width = int(self.orig_width * self.scale)
        # sets self.width to that unless width = 0
        # in which case it is only set if self.orig_width = 0, otherwise it is set to 1
        self.width = width if width or not self.orig_width else 1

        self.border_radius = int(self.orig_border_radius * self.scale)

    # public attributes
    # everything in general UI
    # .color > (r, g, b)
    # .width > integer


class ImageBox(UI):
    def __init__(self, location, image):
        if type(image) != pygame.Surface:
            raise TypeError("Imagebox.image must be a pygame.Surface")
        self.__dict__["orig_image"] = image.copy()
        self.__dict__["image"] = image

        super().__init__(location)

    def _display(self, screen):
        rect = self.location.resolve()
        screen.blit(self.image, (rect.x, rect.y))

    def _get_content_size(self):  # should this return image or orig_image size??
        return self.image.get_size()

    def _scale(self):
        self.__dict__["image"] = image.scale(self.orig_image, self.scale)

    def __setattr__(self, name, value):
        if name == "image":
            if type(value) != pygame.Surface:
                raise TypeError("Imagebox.image must be a pygame.Surface")
            self.__dict__["orig_image"] = value.copy()
            self.__dict__["image"] = value
            self._scale()

        else:
            self.__dict__[name] = value

    # public attributes
    # everything in general UI
    # .image > pygame.Surface


class TextBox(UI):
    def __init__(self, location, textobj, *args):
        self.text = textobj
        self.orig_size = textobj.size

        super().__init__(location, *args)

    def _display(self, screen):
        if self.size_sources[0] == "location":
            self.text.limit = self.location.resolve().w

        rect = self.location.resolve()
        screen.blit(self.text.get_image(), (rect.x, rect.y))

    def __getattr__(self, name):
        # why color and not other text attributes?
        # color b/c consistency with other elements, like box
        # why not other text attributes?
        """
        TODO: achievable by multiple inheritance of UI and Text
        """
        if name == "color":
            return self.text.color
        return self.__dict__[name]

    def __setattr__(self, name, value):
        if name == "color":
            self.text.color = value
        else:
            self.__dict__[name] = value

    def _get_content_size(self):
        return tuple(self.text.get_rect()[2:4])

    def _scale(self):
        self.text.size = self.orig_size * self.scale

    # public attributes
    # everything in general UI
    # .text > pgx.Text
    # .color > (r,g,b), can be used to read or change color of text object


"""
shading has awkward implementation (see __init__ comment)
I think it's fixable as long as it stores whether it was shaded last tick or not
"""


class Button(UI):
    # kwargs
    # on_click < function or None, (default None) callback function for button to call when clicked
    # shade < (r,g,b), (default None)
    # when hovered, changes color attribute of first component to shading color, (works for TextBox and Box)
    def __init__(self, location, *args, **kwargs):
        super().__init__(location, *args)

        self.on_click = None if "on_click" not in kwargs else kwargs["on_click"]

        # this locks down changing the color on the fly other ways after creation
        self.shade = False if "shade" not in kwargs else kwargs["shade"]
        if self.shade:
            self.shade_first_color = self.get_components()[0].color

        self.clicked = False  # accessing .clicked should be valid on a button that hasn't yet been displayed
        self.hovered = False  # same with .hovered

    def _display(self, screen):
        clickrect = self.location.resolve()

        # checking if clicked
        self.clicked = False
        for event in events.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clickrect.collidepoint(pygame.mouse.get_pos()):
                    if (
                        self.on_click
                    ):  # calling specified function for click, if it exists
                        self.on_click()
                    self.clicked = True

        # checking if hovered
        self.hovered = False
        if self.clicked:
            self.hovered = True
        self.hovered = clickrect.collidepoint(pygame.mouse.get_pos())

        # shading if hovered
        if self.hovered and self.shade:
            self.get_components()[0].color = self.shade
        # unshading if not hoverd
        elif not self.hovered and self.shade:
            self.get_components()[0].color = self.shade_first_color

    # public attributes
    # everything in general UI
    # .clicked > boolean, if clicked in last tick (read only)
    # .hovered > boolean, if hovered in last tick (read only)


class Drawing(UI):
    mappings = {
        pygame.draw.rect: shape.Rect,
        pygame.draw.polygon: shape.Polygon,
        pygame.draw.circle: shape.Circle,
        pygame.draw.ellipse: shape.Ellipse,
        pygame.draw.arc: shape.Arc,
        pygame.draw.line: shape.Line,
        pygame.draw.lines: shape.Lines,
        pygame.draw.aaline: shape.AALine,
        pygame.draw.aalines: shape.AALines,
    }

    def __init__(self, location, function, args):
        if function in Drawing.mappings:
            self.shape = Drawing.mappings[function](*args)
        else:
            raise ValueError(f"Function {function.__name__} not supported")

        super().__init__(location)

        self.shape.set_topleft(self.location.resolve()[0:2])
        self.offset = self.shape.get_topleft()

    def _display(self, screen):
        if self.offset != self.location.resolve()[0:2]:
            self.shape.set_topleft(self.location.resolve()[0:2])
            self.offset = self.shape.get_topleft()

        self.shape.display(screen)

    def _get_content_size(self):
        return self.shape.get_size()

    def _scale(self):
        self.shape.scale_to(self.scale)


class Row(Panel):
    def __init__(self, location, *args):
        super().__init__(location, *args)
        self._process_args(*args)

    def _process_args(self, *args):
        for i, arg in enumerate(args):
            if i != 0:
                other = args[i - 1].location.get_resolved_base_rect(True)
                arg.location.x += other.right

        other = args[-1].location
        self.location.w = other.x + other.w

        top = 100000000000000
        bottom = -100000000000000

        for arg in args:
            resolved_rect = arg.location.get_resolved_base_rect(True)
            top = min(resolved_rect.top, top)
            bottom = max(resolved_rect.bottom, bottom)

        self.location.y -= top
        self.location.h = -top + bottom

        for arg in args:
            arg.location.y -= top

    def add_component(self, *args):
        raise NotImplementedError("Rows don't know how to add components right now")


class Column(Panel):
    def __init__(self, location, *args):
        super().__init__(location, *args)
        self._process_args(*args)

    def _process_args(self, *args):
        for i, arg in enumerate(args):
            if i != 0:
                other = args[i - 1].location.get_resolved_base_rect(True)
                arg.location.y += other.bottom

        other = args[-1].location
        self.location.h = other.y + other.h

        left = 100000000000000
        right = -100000000000000

        for arg in args:
            resolved_rect = arg.location.get_resolved_base_rect(True)
            left = min(resolved_rect.left, left)
            right = max(resolved_rect.right, right)

        self.location.x -= left
        self.location.w = -left + right

        for arg in args:
            arg.location.x -= left

    def add_component(self, *args):
        raise NotImplementedError("Columns don't know how to add components right now")
