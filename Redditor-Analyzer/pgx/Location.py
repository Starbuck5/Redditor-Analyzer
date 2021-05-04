import copy

import pygame

from pgx.interpret_coords import interpret_coords
from pgx.scale import scale

from pgx.Rect import Rect as pgx_rect
from pygame import Rect as pygame_rect


class Location:
    def __init__(self, *args, **kwargs):
        # processing alternative forms of init
        if len(args) == 0:
            rect = [0, 0, -1, -1]
            align = "left"
        elif len(args) == 1:
            rect = args[0]
            align = "left"
        elif len(args) == 2:
            rect, align = args
        else:
            raise TypeError(
                f"Location takes 0-2 parameters but {len(args)} parameters were given"
            )

        try:
            rect = list(rect)
            if len(rect) == 2:
                rect += [-1, -1]
            if len(rect) == 3:
                rect += [-1]
        except:
            raise TypeError("Location rect arg must be a list-esque thing (a sequence)")

        precise = False if "precise" not in kwargs else kwargs["precise"]
        if precise:
            self.rect_class = pgx_rect
        else:
            self.rect_class = pygame_rect

        self.align = align
        self._base_rect_num, self._base_rect_keywords = self._uncombine_rect(rect)
        self.changed = False

        self._ui_scale = 1
        self._user_scale = 1

        self._base_panel_dim = self.rect_class([0, 0, *scale.get_resolution()])
        self.last_offset = scale.get_offset()

        self._resolve()

    def __str__(self):
        self.resolve()
        return f"Location: {self.get_resolved_base_rect()} -> {self.resolve()}, ui_scale: {self.get_ui_scale()}, user_scale: {self.get_user_scale()}"

    def __eq__(self, other):
        return self.resolve() == other.resolve()

    # ------------------------------------------------------------------------------------------#
    #                                          HELPER METHODS                                   #
    # ------------------------------------------------------------------------------------------#

    # method to take formatted rects with keywords in them and split them into
    # their keywords and numbers separately
    def _uncombine_rect(self, rect):
        rect_num = [0, 0, 0, 0]
        rect_keywords = ["", "", "", ""]

        for i, term in enumerate(rect):
            try:
                rect_num[i] = int(term)
            except:
                term = "".join(
                    [char if char not in ["+", "-"] else " " + char for char in term]
                )
                subterms = term.split(" ")

                for subterm in subterms:
                    try:
                        rect_num[i] += int(subterm)
                    except:
                        rect_keywords[i] += subterm

        return self.rect_class(rect_num), rect_keywords

    # method that reconstitutes a formatted rect out of the keywords and numbers
    # extracted earlier
    def _combine_rect(self, rect_num, rect_keywords):
        rect_output = ["", "", "", ""]
        for i, (num, keyword) in enumerate(zip(rect_num, rect_keywords)):
            if keyword:
                rect_output[i] = keyword + "+" + str(num)
            else:
                rect_output[i] = num

        return rect_output

    def _scale_rect(self, rect, pos_scale, size_scale):
        rect.x *= pos_scale
        rect.y *= pos_scale
        rect.w *= size_scale
        rect.h *= size_scale

    def _resolve(self):
        # keeping track of things that control when to resolve
        self._last_base_rect_num = self._base_rect_num.copy()
        self.changed = False
        self.last_offset = scale.get_offset()

        # generating self.current_rect_resolved
        current_rect_num = self._base_rect_num.copy()
        self._scale_rect(
            current_rect_num,
            self.get_ui_scale(),
            self.get_ui_scale() * self.get_user_scale(),
        )
        current_rect_formatted = self._combine_rect(
            current_rect_num, self._base_rect_keywords
        )

        scaled_panel_dim = self._base_panel_dim.copy()
        self._scale_rect(scaled_panel_dim, self.get_ui_scale(), self.get_ui_scale())

        interpret_coords(current_rect_formatted, self.get_align(), scaled_panel_dim)
        # current resolved rect uses pygame_rects because resolved coordinates are used on the screen
        # so sub pixel detail doesn't matter anymore
        self._current_rect_resolved = pygame_rect(current_rect_formatted)

        # generating self._base_rect_resolved
        # gives UI scaling something firm to grab (in pgx.ui.UI.display())
        # has to take into account user directed scaling separately than ui scaling
        base_rect_num_scaled = self._base_rect_num.copy()
        self._scale_rect(base_rect_num_scaled, 1, self.get_user_scale())

        base_rect_formatted = self._combine_rect(
            base_rect_num_scaled, self._base_rect_keywords
        )

        interpret_coords(
            base_rect_formatted, self.get_align(), self.get_parent_context(), True
        )
        self._base_rect_resolved = self.rect_class(base_rect_formatted)

    # ------------------------------------------------------------------------------------------#
    #                                 PANEL_DIM CONTEXT INTERFACE                               #
    # ------------------------------------------------------------------------------------------#

    def get_parent_context(self):
        return self._base_panel_dim

    def set_parent_context(self, value):
        value = self.rect_class(value)

        if value != self._base_panel_dim:
            self.changed = True

        self._base_panel_dim = value

    # ------------------------------------------------------------------------------------------#
    #                                     ALIGN INTERFACE                                       #
    # ------------------------------------------------------------------------------------------#

    def get_align(self) -> str:
        """Get the align (“left”, “right”, or “center”)."""
        return self.align

    def set_align(self, align: str) -> None:
        """Set the align (“left”, “right”, or “center”)."""
        if align != self.align:
            self.changed = True

        self.align = align

    # ------------------------------------------------------------------------------------------#
    #                                     SCALE INTERFACE                                       #
    # ------------------------------------------------------------------------------------------#

    def get_ui_scale(self) -> float:
        return self._ui_scale

    def set_ui_scale(self, value: float) -> None:
        if value != self._ui_scale:
            self.changed = True

        self._ui_scale = value

    def get_user_scale(self) -> float:
        return self._user_scale

    def set_user_scale(self, value: float) -> None:
        if value != self._user_scale:
            self.changed = True

        self._user_scale = value

    # ------------------------------------------------------------------------------------------#
    #                                     RECT INTERFACE                                        #
    # ------------------------------------------------------------------------------------------#

    rect_methods = {"move_ip", "inflate_ip", "clamp_ip"}
    rect_attributes = {
        "y",
        "h",
        "left",
        "right",
        "bottom",
        "center",
        "topleft",
        "centerx",
        "topright",
        "midbottom",
        "bottomright",
        "bottomleft",
        "midright",
        "centery",
        "midleft",
        "height",
        "midtop",
        "width",
        "size",
        "top",
        "w",
        "x",
    }

    def __getattr__(self, name):
        if name in Location.rect_attributes or name in Location.rect_methods:
            return getattr(self._base_rect_num, name)

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name, value):
        if name in Location.rect_attributes:
            setattr(self._base_rect_num, name, value)
        else:
            self.__dict__[name] = value

    # ------------------------------------------------------------------------------------------#
    #                                    RESULTS INTERFACE                                      #
    # ------------------------------------------------------------------------------------------#

    def resolve(self, force_processing=False):
        """Returns the resolved rect of the location object."""
        if (
            self.changed
            or self.last_offset != scale.get_offset()
            or force_processing
            or self._last_base_rect_num != self._base_rect_num
        ):
            self._resolve()

        return self._current_rect_resolved

    def get_resolved_base_rect(self, force_processing=False):
        """Returns a rect that takes into account everything but system UI scaling."""
        if force_processing:
            self._resolve()

        return self._base_rect_resolved

    def visualize(
        self, screen: pygame.Surface = None, color=(255, 0, 0), width: int = 1
    ) -> None:
        """Handy way of seeing what the location is thinking."""
        if not screen:
            screen = pygame.display.get_surface()

        pygame.draw.rect(screen, color, self.resolve(), width)

    def copy(self):
        return copy.deepcopy(self)
