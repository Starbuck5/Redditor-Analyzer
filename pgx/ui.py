import pygame
import copy

from pgx.events import events
from pgx.key import key
from pgx.time import time
from pgx.Text import Text
from pgx.Location import Location
from pgx.data import data
from pgx.image import image

from abc import ABC

"""
should change panel_dim param of _display methods to rect,
process location to rect once and then pass to everything else

also need to add get_size methods to everything and make sure that
avenue is all squared away (with proper location of super().__init__ in subclasses

add slider to __all__ when it is ready for prime time
"""

__all__ = [
    "UI",
    "Panel",
    "Box",
    "ImageBox",
    "Button",
    "InputGetter",
    "ToggleBox",
    "Drawing",
    "Row",
    "Column",
]


# WHAT AN UI ELEMENT NEEDS
# ._display(self,screen)
# call to super().__init__(location, components)
# get_size() method
# Consider implementing a ._scale(self) to handle size changes


class UI(ABC):
    def __init__(self, location, *args):
        self.visible = True

        self.location = location
        self.components = list(args)

        # if not given a location with a width and height, it attempts to set it
        if self.location.rect.w == 0 and self.location.rect.h == 0:
            # first it checks if this subclass has a get size method that returns a different, more accurate value
            size = self.get_size()
            if size[0] or size[1]:
                rect = self.location.rect
                rect[2:4] = size
                self.location.rect = rect

            # if it can't do that it checks it's component list to determine size from the first added element
            elif self.components:
                if self.components[0].get_size()[0] or self.components[0].get_size()[1]:
                    # self.location.rect[2:4] = self.components[0].get_size()
                    rect = self.location.rect
                    rect[2:4] = self.components[0].get_size()
                    self.location.rect = rect

        self.base_scale = data.get_global_scale()
        self.user_scale = 1
        self.scale = 1

    def display(self, screen=None, panel_dim=None):
        if not screen:
            screen = pygame.display.get_surface()

        self.base_scale = data.get_global_scale()
        scale = self.base_scale * self.user_scale
        if self.scale != scale:
            self.scale = scale
            self._scale()  # process
        self.location.scale = self.scale
        self.location.panel_dim = panel_dim

        if self.visible:
            rect = self.location.resolve()

            self._display(screen, panel_dim)

            for component in self.components:
                # base_rect represents a newly resolved panel dimension
                # everything on this layer of abstraction is using unscaled number
                component.display(screen, self.location.base_rect)

    def add(self, *args):
        self.components += list(args)

    def copy(self):
        return copy.deepcopy(self)

    def get_size(self):
        return self.location.resolve()[2:4]

    def get_components(self):
        return self.components

    def clear_components(self):
        self.components = []

    # should be overwritten
    def _scale(self):
        # print(f"Generic _scale called: {self.__class__}")
        pass

    """future:"""
    """Calling _scale or _display on a UI object that has not defined those with result in an exception being raised"""

    # public attributes
    # .location > pgx.Location object
    # .visible > boolean, controls whether object draws or not
    # .user_scale > individual scale of the element, automatically combined with global scale


class Panel(UI):
    def _display(self, screen, rect):
        pass

    # public attributes
    # everything in general UI


class Box(UI):
    def __init__(self, location, color, width=0):
        super().__init__(location)
        self.color = color
        self.orig_width = width
        self.width = width

    def _display(self, screen, panel_dim=None):
        rect = self.location.resolve()
        pygame.draw.rect(screen, self.color, rect, self.width)

    def _scale(self):
        # adjusts original width by the scale
        width = int(self.orig_width * self.scale)
        # sets self.width to that unless width = 0
        # in which case it is only set if self.orig_width = 0, otherwise it is set to 1
        self.width = width if width or not self.orig_width else 1

    # public attributes
    # everything in general UI
    # .color > (r, g, b)
    # .width > integer


class ImageBox(UI):
    def __init__(self, location, image):
        self.__dict__["orig_image"] = image.copy()
        self.__dict__["image"] = image

        super().__init__(location)

    def _display(self, screen, panel_dim=None):
        rect = self.location.resolve()
        screen.blit(self.image, (rect.x, rect.y))

    def get_size(self):  # should this return image or orig_image size??
        return self.image.get_size()

    def _scale(self):
        self.__dict__["image"] = image.scale(self.orig_image, self.scale)

    def __setattr__(self, name, value):
        if name == "image":
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

    def _display(self, screen, panel_dim=None):
        # updating width and height from possible text changes
        rect = self.location.rect
        rect[2:4] = self.text.get_rect()[2:4]
        rect[2] /= self.scale  # stops this from malfunctioning
        rect[3] /= self.scale  # at different scales
        self.location.rect = rect

        rect = self.location.resolve()
        # print(self.text.text, panel_dim, rect)
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

    def get_size(self):
        return self.text.get_rect()[2:4]

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

    def _display(self, screen, panel_dim=None):
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


class InputGetter(TextBox):
    # kwargs
    # length_limit < int, (default None) maximum length of the text
    # delete_start < boolean, (default True) delete starting text on first input or not
    # input_type
    # allowed_chars
    def __init__(self, location, textobj, *args, **kwargs):
        super().__init__(location, textobj, *args)
        self.initial_text = self.text.text

        # kwarg settings
        self.input_type = "all" if "input_type" not in kwargs else kwargs["input_type"]
        if self.input_type not in ["abc", "int", "all"]:
            raise ValueError("input type can only be 'abc', 'int', or 'all' (default)")

        if "length_limit" in kwargs:
            if not isinstance(kwargs["length_limit"], int):
                raise TypeError("length_limit must be an int")

        self.length_limit = (
            None if "length_limit" not in kwargs else kwargs["length_limit"]
        )

        # stores whether it should delete at when it gets input
        self.del_after_input = (
            True if "delete_start" not in kwargs else kwargs["delete_start"]
        )

        self.del_after_input_setting = (
            False
            if "delete_start_always" not in kwargs or not kwargs["delete_start_always"]
            else self.del_after_input
        )

        self.allowed_chars = (
            False if "allowed_chars" not in kwargs else kwargs["allowed_chars"]
        )

        # initializing responding variables
        self.clicked = False

        # blink controls and state
        self.blinking = True
        self.blink_on = False  # whether blink is currently on
        self.blink_time = 0.6
        self.blink_timer = 0
        self.blink_box = Box(Location(), self.text.color, 0)  # moved in code later

    def _display(self, screen, panel_dim=None):
        super()._display(screen, panel_dim)

        self._handle_blinks(screen, panel_dim)
        self._handle_clicks(panel_dim)
        if self.clicked:
            self._handle_input()

    def _handle_blinks(self, screen, panel_dim):
        if self.blinking:
            self.blink_timer -= time.delta_time
            if self.blink_timer < 0:
                self.blink_timer = self.blink_time
                self.blink_on = not self.blink_on

            if self.blink_on and self.clicked:
                text_loc = self.location.base_rect
                self.blink_box.location = Location(
                    [text_loc[0] + text_loc[2] + 2, text_loc[1], 2, text_loc[3]]
                )
                self.blink_box.display(screen)

    def _handle_clicks(self, panel_dim=None):
        clickrect = self.location.resolve()

        for event in events.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clickrect.collidepoint(*pygame.mouse.get_pos()):
                    if not self.clicked:
                        self.clicked = True
                        if not self.del_after_input:
                            self.del_after_input = self.del_after_input_setting

                elif self.clicked:
                    self.clicked = False
                    if (
                        len(self.text.text) == 0
                    ):  # if you click off when it has nothing it will reset
                        self.text.text = self.initial_text

    def _handle_input(self):
        for event in key.downevents():
            # with any input it deletes what it has
            if self.del_after_input:
                self.del_after_input = False
                self.text.text = ""

            # deleting text on backspace
            if event.key == pygame.K_BACKSPACE and len(self.text) != 0:
                self.text.text = self.text.text[:-1]

            # adding text
            if not self.length_limit or len(self.text.text) < self.length_limit:
                if event.unicode:
                    if event.key not in [
                        pygame.K_BACKSPACE,
                        pygame.K_RETURN,
                        pygame.K_TAB,
                    ] and (
                        self.allowed_chars == False
                        or event.unicode in self.allowed_chars
                    ):
                        # we can add the input to the text, assuming it fits
                        if self.input_type == "all":
                            self.text.text += event.unicode
                        elif self.input_type == "abc":
                            if event.unicode.isalpha():
                                self.text.text += event.unicode
                        elif self.input_type == "int":
                            if event.unicode.isdigit():
                                self.text.text += event.unicode

    def __getattr__(self, name):
        if name == "length":
            return len(self.__dict__["text"].text)
        if name == "changed":
            return self.initial_text != self.text.text
        return self.__dict__[name]

    # public attributes
    # everything in general UI
    # .clicked > boolean, whether it has been clicked on and is accepting text input
    # .length > int, length of resident text (read only)
    # .initial_text > str, the starting text of the inputgetter (read only)
    # .changed > if current text != initial text (read only)


class ToggleBox(Button):
    def __init__(self, location, always, off, on, **kwargs):
        super().__init__(location, always, off, on, **kwargs)

        self.always = always
        self.off = off
        self.on = on

        self.state = False  # setting state makes _adjust_visibility called

    def _adjust_visibility(self):
        if self.state:
            self.off.visible = False
            self.on.visible = True
        else:
            self.off.visible = True
            self.on.visible = False

    def _display(self, screen, panel_dim):
        super()._display(screen, panel_dim)
        if self.clicked:
            self.state = not self.state
            self._adjust_visibility()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        if name == "state":
            self._adjust_visibility()

    # public attributes
    # everything in button
    # .state > boolean, whether it is toggled on or off


class Drawing(UI):
    def __init__(self, location, function, args):
        self.function = function
        self.orig_args = self._configure_args(args)
        self.args = copy.deepcopy(self.orig_args)
        super().__init__(location)
        self._scale()

    def _display(self, screen, panel_dim):
        # explanation of this gnarly line of code:
        # position the scaled, real version of the arguments given
        # convert to a dict and get the values
        # (cool way of grabbing the second element of all sequences in a list of sequences)
        self.function(screen, *dict(self._position_args(self.args)).values())
        # it's not great that it has to reposition each tick, but its okay

    def _configure_args(self, vals):
        # not actual argument signature - changed to reflect how they should be dealt with
        # in scaling and in positioning
        if self.function == pygame.draw.rect:
            args = ["color", "rect", "width"]
        if self.function == pygame.draw.polygon:
            args = ["color", "points", "width"]
        elif self.function == pygame.draw.circle:
            args = ["color", "point", "width", "width"]
        elif self.function == pygame.draw.ellipse:
            args = ["color", "rect", "width"]
        elif self.function == pygame.draw.arc:
            args = ["color", "rect", "start_angle", "stop_angle", "width"]
        elif self.function == pygame.draw.line:
            args = ["color", "start_pos", "end_pos", "width"]
        elif self.function == pygame.draw.lines:
            args = ["color", "closed", "points", "width"]
        elif self.function == pygame.draw.aaline:
            args = ["color", "point", "point", "blend"]
        elif self.function == pygame.draw.aalines:
            args = ["color", "closed", "points", "blend"]
        else:
            raise ValueError(f"Function {self.function} not supported")
        return list(zip(args, vals))

    def _position_args(self, args):
        args = list(args)  # basically a copy operation
        lrect = self.location.resolve()
        lrect[0] = int(lrect[0])
        lrect[1] = int(lrect[1])
        for i, (arg, val) in enumerate(args):
            if arg == "rect":
                args[i] = (arg, lrect)
            if arg == "point":
                args[i] = (arg, self._translate_points([val], lrect)[0])
            if arg == "points":
                args[i] = (arg, self._translate_points(val, lrect))
        return args

    def _scale_points(self, points):
        new_points = []
        for point in points:
            x, y = point
            x *= self.scale
            y *= self.scale
            x = int(x)
            y = int(y)
            new_points.append((x, y))
        return new_points

    def _translate_points(self, points, translation):
        new_points = []
        for point in points:
            x, y = point
            x += translation[0]
            y += translation[1]
            new_points.append((x, y))
        return new_points

    def _scale(self):
        for i, (arg, val) in enumerate(self.orig_args):
            if arg == "width":
                width = int(val * self.scale)
                self.args[i] = (arg, width) if width or not val else (arg, 1)
            elif arg == "point":
                self.args[i] = (arg, self._scale_points([val])[0])
            elif arg == "points":
                self.args[i] = (arg, self._scale_points(val))

    """
    NEEDS A GET_SIZE
    def get_size(self):
        points = []
        for arg in self.args:
            if arg == 'rect':
                return self.args[2:4]
            if arg == 'point':
                points.append(self.args[arg])
    """

    def get_size(self):
        arguments = self.orig_args
        argument_types = dict(self.orig_args).keys()
        if self.function == pygame.draw.circle:
            return [arguments[2][1] * 2, arguments[2][1] * 2]
        if "rect" in argument_types:
            return dict(arguments)["rect"]
        return [0, 0]

    # public attributes
    # everything in general UI
    # .function > whatever function the drawing is calling to display itself (read only)


"""
What if I wanted a vertical slider?
"""


class Slider(UI):
    # kwargs
    # start_pos < int (0 <= start_pos <= 100)
    def __init__(self, location, bar, selector, *args, **kwargs):
        super().__init__(location, bar, selector, *args)
        # self.bar = bar
        self.selector = selector

        self.percent = 0 if "start_pos" not in kwargs else kwargs["start_pos"]

        self.selected = False

        self.unhandled_change = 0.0  # rect dimensions can only be ints, meaning it loses precision when scaling

    def _position_selector(self):
        for event in events.get():
            if event.type == pygame.MOUSEMOTION:
                rel = event.rel[0] / self.scale
                rel += self.unhandled_change
                int_rel = int(rel)
                self.unhandled_change = rel - int_rel

                r = self.selector.location.rect
                r = r.move(int_rel, 0)

                if r[0] < 0:
                    r[0] = 0

                if r[0] + r[2] > self.location.rect[2]:
                    r[0] = self.location.rect[2] - r[2]

                self.percent = int(r[0] / (self.location.rect[2] - r[2]) * 100)

                self.selector.location.rect = r

    def _display(self, screen, panel_dim):
        if self.selector.clicked:
            self.selected = True

        if self.selected:
            self._position_selector()

            for event in events.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    self.selected = False

    def _set_percent(self, percent):
        if percent < 0 or percent > 100:
            raise ValueError("Percent must be between 0 and 100")

        r = self.selector.location.rect
        r[0] = int(percent / 100 * (self.location.rect[2] - r[2]))
        self.selector.location.rect = r

        self.__dict__["percent"] = int(percent)

    def __setattr__(self, name, value):
        if name == "percent":
            self._set_percent(value)
        else:
            self.__dict__[name] = value

    # public attributes
    # everything in general UI
    # .percent > int 0<=n<=100 (read and writeable)


"""
is it possible to use aligns in this current setup?
would it be possible to use resolved locations rather than base offsets
to allow offsets of anchors and aligns?
"""


class Row(Panel):
    def __init__(self, location, *args):
        super().__init__(location, *args)

        for i, arg in enumerate(args):
            crect = arg.location.rect
            if i == 0:
                pass
            else:
                other = args[i - 1].location.rect
                crect[0] += other[0] + other[2]
            arg.location.rect = crect

        rect = self.location.rect
        rect[2] = args[-1].location.rect[0] + args[-1].location.rect[2]
        self.location.rect = rect


class Column(Panel):
    def __init__(self, location, *args):
        super().__init__(location, *args)

        for i, arg in enumerate(args):
            crect = arg.location.rect
            if i == 0:
                pass
            else:
                other = args[i - 1].location.rect
                crect[1] += other[1] + other[3]
            arg.location.rect = crect

        rect = self.location.rect
        rect[3] = args[-1].location.rect[1] + args[-1].location.rect[3]
        self.location.rect = rect
