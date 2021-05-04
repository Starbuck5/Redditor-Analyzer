import webbrowser

import pygame

from pgx.Location import Location
from pgx.time import time
from pgx.key import key
from pgx.events import events
from pgx._scrap import scrap

from pgx.ui.UI import UI
from pgx.ui.base import *
from pgx.ui.component import *
from pgx.ui.constants import *


__all__ = ["InputGetter", "ToggleBox", "Slider", "Link", "InputBox"]

# helper for tracking changes for ctrl-z and ctrl-y in inputgetters
class ChangesTracker:
    def __init__(self, start):
        self.values = [start]
        self.index = 0

    def add(self, val):
        self.index += 1
        del self.values[self.index :]
        self.values.append(val)

    def forward(self):
        self.index += 1
        if self.index > len(self.values) - 1:
            self.index = len(self.values) - 1
        return self.values[self.index]

    def back(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
        return self.values[self.index]

    def see_current(self):
        return self.values[self.index]


class InputBox(UI):
    def __init__(self, location, textobj, *args, **kwargs):
        self.textbox = TextBox(location, textobj)
        self.text = textobj

        self.initial_text = textobj.text
        self.changes = ChangesTracker(self.initial_text)

        if "length_limit" in kwargs:
            if not isinstance(kwargs["length_limit"], int):
                raise TypeError("length_limit must be an int")

        self.length_limit = (
            None if "length_limit" not in kwargs else kwargs["length_limit"]
        )

        self.clicked = False

        self.allowed = INPUT_DEFAULT if "allowed" not in kwargs else kwargs["allowed"]
        self.prohibited = (
            INPUT_SPECIALS if "prohibited" not in kwargs else kwargs["prohibited"]
        )

        self.selectable = False

        # cursor controls and state
        self.cursor_visible = True
        self.cursor_blinktime = 0.6
        self.cursor_timer = 0
        self.cursor_index = 5

        if not scrap.get_init():
            scrap.init()

        super().__init__(location, *args)

    def _display(self, screen):
        self._update_clicked()
        if self.clicked:
            self._update_text()

        self.textbox.display(screen)

        # cursor display goes over (after) textbox display
        if self.clicked:
            self._update_text_cursor(screen)

    def _update_clicked(self):
        clickrect = self.location.resolve()

        for event in events.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if clickrect.collidepoint(pygame.mouse.get_pos()):
                    self.clicked = True
                    self._on_click_on()

                else:
                    self.clicked = False
                    self._on_click_off()

    def _on_click_on(self):
        m = self.text.get_rect_metrics()
        pos_off = self.location.resolve()
        mouse_pos = list(pygame.mouse.get_pos())

        # aligns mouse to relative metrics position rather than the other way around
        mouse_pos[0] -= pos_off[0]
        mouse_pos[1] -= pos_off[1]

        cursor_index = len(self.text.text)  # backup value
        for i, rm in enumerate(m):
            if rm.collidepoint(mouse_pos):
                cursor_index = i
                break

        self.cursor_index = cursor_index

    def _on_click_off(self):
        # shouldn't be possible to leave a blank zero area box
        if self.text.text.strip() == "":
            self.text.text = self.initial_text

        # resetting text cursor stuff so it pops up promptly
        self.cursor_timer = 0
        self.cursor_visible = True

    def _update_text_cursor(self, screen):
        self.cursor_timer += time.delta_time
        if self.cursor_timer > self.cursor_blinktime:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            m = self.text.get_rect_metrics()

            if m:
                if self.cursor_index == 0:
                    x, y = m[self.cursor_index][0:2]

                else:
                    r = m[self.cursor_index - 1]
                    x = r.right
                    y = r.y

                xoff, yoff = self.location.resolve()[0:2]

                x += xoff
                y += yoff

                height = self.text.size
                width = int(height / 25) or 1
                color = self.text.color

                pygame.draw.rect(screen, color, [x, y, width, height])

    # bounded addition / subtraction for text cursor
    def _move_text_cursor(self, movement):
        self.cursor_index += movement

        if self.cursor_index < 0:
            self.cursor_index = 0
        if self.cursor_index > len(self.text.text):
            self.cursor_index = len(self.text.text)

    def _update_text(self):
        for event in key.get_all_events():
            char = event.unicode
            mod = event.mod

            # paste support (ctrl-v)
            if event.key == pygame.K_v and mod & key.MOD:
                k = scrap.get(pygame.SCRAP_TEXT)
                self._add_chars(k)

            # undo support (ctrl-z)
            elif event.key == pygame.K_z and mod & key.MOD:
                self.text.text = self.changes.back()
                self._move_text_cursor(0)

            # redo support (ctrl-y)
            elif event.key == pygame.K_y and mod & key.MOD:
                self.text.text = self.changes.forward()
                self._move_text_cursor(0)

            # copy support (ctrl-c) - (only applicable w/ Selectable)
            elif event.key == pygame.K_c and mod & key.MOD:
                # gives pgx.key the ctrl-c event back so it can be picked up later by Selectable
                key.add_event(event)

            # cut support (ctrl-x) - (only applicable w/ Selectable)
            elif event.key == pygame.K_x and mod & key.MOD:
                if self.selectable:
                    r = self.selectable.get_bounds()
                    if r:
                        t = list(self.text.text)
                        contents = "".join(t[slice(r[0], r[-1] + 1)])

                        del t[slice(r[0], r[-1] + 1)]
                        self.text.text = "".join(t)
                        self.cursor_index = r[
                            0
                        ]  # setting the cursor to start of modified section

                        scrap.put(pygame.SCRAP_TEXT, contents)

            # select all support (ctrl-a) - (only applicable w/ Selectable)
            elif event.key == pygame.K_a and mod & key.MOD:
                if self.selectable:
                    b = [0, len(self.text.text)]
                    self.selectable.set_bounds(b)

            # deleting text on backspace
            elif event.key == pygame.K_BACKSPACE and len(self.text.text) != 0:
                r = False
                if self.selectable:
                    r = self.selectable.get_bounds()

                if r:
                    t = list(self.text.text)
                    del t[slice(r[0], r[-1] + 1)]
                    self.text.text = "".join(t)
                    self.cursor_index = r[
                        0
                    ]  # setting the cursor to start of modified section
                else:
                    textlist = list(self.text.text)
                    textlist = (
                        textlist[: max(self.cursor_index - 1, 0)]
                        + textlist[self.cursor_index :]
                    )
                    self.text.text = "".join(textlist)
                    self._move_text_cursor(-1)

            # deleting text on delete
            elif event.key == pygame.K_DELETE:
                r = False
                if self.selectable:
                    r = self.selectable.get_bounds()

                if r:
                    t = list(self.text.text)
                    del t[slice(r[0], r[-1] + 1)]
                    self.text.text = "".join(t)
                    self.cursor_index = r[
                        0
                    ]  # setting the cursor to start of modified section
                else:
                    textlist = list(self.text.text)
                    textlist = (
                        textlist[: max(self.cursor_index, 0)]
                        + textlist[self.cursor_index + 1 :]
                    )
                    self.text.text = "".join(textlist)

            # cursor movements
            elif event.key == pygame.K_LEFT:
                self._move_text_cursor(-1)
                # resetting text cursor stuff so it pops up promptly
                self.cursor_timer = 0
                self.cursor_visible = True

            elif event.key == pygame.K_RIGHT:
                self._move_text_cursor(1)
                # resetting text cursor stuff so it pops up promptly
                self.cursor_timer = 0
                self.cursor_visible = True

            # normal text
            elif not mod & key.MOD and char:
                self._add_chars([char])

        if self.changes.see_current() != self.text.text:
            self.changes.add(self.text.text)

    def _add_chars(self, chars):
        textlist = list(self.text.text)
        cursor_index = self.cursor_index

        if self.selectable:
            r = self.selectable.get_bounds()
            if r:
                del textlist[slice(r[0], r[-1] + 1)]
                cursor_index = r[0]

        for char in chars:
            prohibited = char in self.prohibited  # prohibited char
            allowed = char in self.allowed  # allowed char
            allowed = True

            # whether another character can be added
            length = not self.length_limit or len(self.text.text) < self.length_limit

            if not prohibited and allowed and length:
                textlist[cursor_index:cursor_index] = char
                cursor_index += 1

        self.text.text = "".join(textlist)
        self.cursor_index = cursor_index

    def _get_content_size(self):
        return tuple(self.text.get_rect()[2:4])

    def add_components(self, *args):
        args = list(args)

        for component in args:
            if isinstance(component, Selectable):
                self.selectable = component

        super().add_components(*args)


class InputGetter(TextBox):
    # kwargs
    # length_limit < int, (default None) maximum length of the text
    # delete_start < boolean, (default True) delete starting text on first input or not
    # input_type
    # allowed_chars
    def __init__(self, location, textobj, *args, **kwargs):
        super().__init__(location, textobj, *args)
        self.initial_text = self.text.text
        self.changes = ChangesTracker(self.initial_text)

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
        self.blink_box = Box(
            Location([0, 0, 2, 0]), self.text.color, 0
        )  # moved in code later

        if not scrap.get_init():
            scrap.init()

    def _display(self, screen):
        super()._display(screen)

        self._handle_blinks(screen)
        self._handle_clicks()
        if self.clicked:
            self._handle_input()

    def _handle_blinks(self, screen):
        if self.blinking:
            self.blink_timer -= time.delta_time
            if self.blink_timer < 0:
                self.blink_timer = self.blink_time
                self.blink_on = not self.blink_on

            if self.blink_on and self.clicked:
                loc = self.location.get_resolved_base_rect()
                self.blink_box.location.x = loc.right + 2
                self.blink_box.location.y = loc.y
                self.blink_box.location.h = loc.h

                self.blink_box.display(screen)

    def _handle_clicks(self):
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
        for event in key.get_text_input_events():
            char = event.unicode
            mod = event.mod

            # with any input it deletes what it has
            if self.del_after_input:
                self.del_after_input = False
                self.text.text = ""

            # paste support (ctrl-v)
            if char == "\x16" and mod & key.MOD:
                k = scrap.get(pygame.SCRAP_TEXT)
                for letter in k:
                    self._handle_text(letter)

            # undo support (ctrl-z)
            elif char == "\x1a" and mod & key.MOD:
                self.text.text = self.changes.back()

            # redo support (ctrl-y)
            elif char == "\x19" and mod & key.MOD:
                self.text.text = self.changes.forward()

            # deleting text on backspace
            elif char == "\b" and len(self.text) != 0:
                self.text.text = self.text.text[:-1]

            # else:
            elif not self.length_limit or len(self.text.text) < self.length_limit:
                is_textchar = char not in ["\b", "\t", "\r", "\n"] and not mod & key.MOD
                is_allowedchar = (
                    self.allowed_chars == False or char in self.allowed_chars
                )
                if is_textchar and is_allowedchar:
                    self._handle_text(char)

        if self.changes.see_current() != self.text.text:
            self.changes.add(self.text.text)

    def _handle_text(self, char):
        if self.input_type == "all":
            self.text.text += char
        elif self.input_type == "abc":
            if char.isalpha():
                self.text.text += char
        elif self.input_type == "int":
            if char.isdigit():
                self.text.text += char

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

    def _display(self, screen):
        super()._display(screen)
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

                r = self.selector.location
                r.x += int_rel

                r.x = 0 if r.x < 0 else r.x
                r.x = self.location.w - r.w if self.location.w < r.x + r.w else r.x

                self.__dict__["percent"] = int(r.x / (self.location.w - r.w) * 100)

    def _display(self, screen):
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

        r = self.selector.location
        r.x = int(percent / 100 * (self.location.w - r.w))

        self.__dict__["percent"] = int(percent)

    def __setattr__(self, name, value):
        if name == "percent":
            self._set_percent(value)
        else:
            self.__dict__[name] = value

    # public attributes
    # everything in general UI
    # .percent > int 0<=n<=100 (read and writeable)


hand_cursor_string = (
    "                        ",
    "         XX             ",
    "        X..X            ",
    "        X..X            ",
    "        X..X            ",
    "        X..X            ",
    "        X..XXX          ",
    "        X..X..XXX       ",
    "        X..X..X..XX     ",
    "        X..X..X..X.X    ",
    "        X..X..X..X..X   ",
    "        X..X..X..X..X   ",
    "        X..X..X..X..X   ",
    "    XX  X...........X   ",
    "   X..X X...........X   ",
    "   X...XX...........X   ",
    "    X...............X   ",
    "     X..............X   ",
    "      X.............X   ",
    "       X............X   ",
    "        X..........X    ",
    "         XX.......X     ",
    "           XXXXXXX      ",
    "                        ",
)

hand_cursor_small = (
    "      X         ",
    "     X.X        ",
    "     X.X        ",
    "     X.X        ",
    "     X.XX       ",
    "     X.X.XX     ",
    "     X.X.X.XX   ",
    "     X.X.X.X.X  ",
    "     X.X.X.X.X  ",
    "     X.......X  ",
    "  XX X.......X  ",
    "  X.XX.......X  ",
    "  X..........X  ",
    "   X.........X  ",
    "    XX......X   ",
    "      XXXXXX    ",
)


class Link(TextBox):
    def __init__(self, location, textobj, link, *args, **kwargs):
        textobj.style &= pygame.freetype.STYLE_UNDERLINE
        self.link = link

        super().__init__(location, textobj)

        self.button = Button(Location([0, 0, "width", "height"]))
        self.add_component(self.button)

        self.change_cursor = (
            True if "change_cursor" not in kwargs else kwargs["change_cursor"]
        )

        self.currently_hovered = False
        self.cursor_data = None

    def _display(self, screen):
        super()._display(screen)

        if self.button.clicked:
            webbrowser.open(self.link)

        if self.change_cursor:
            if self.button.hovered:
                if not self.currently_hovered:
                    self.currently_hovered = True
                    self.cursor_data = pygame.mouse.get_cursor()
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            else:
                if self.currently_hovered:
                    self.currently_hovered = False
                    pygame.mouse.set_cursor(self.cursor_data)

    # public attributes
    # everything in general UI
    # .text > pgx.Text
    # .color > (r,g,b), can be used to read or change color of text object
    # .link > string, the address the link object goes to when clicked.
