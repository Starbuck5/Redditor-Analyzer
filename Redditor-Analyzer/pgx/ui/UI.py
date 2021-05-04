from abc import ABC
import copy
import warnings

import pygame

from pgx.scale import scale
from pgx.time import time

#                          #
# WHAT AN UI ELEMENT NEEDS #
#                          #

# _display(self, screen) method -> None
# implements what the element does when displayed

# call into UI init - super().__init__(location, components)

#                               #
# WHAT AN UI ELEMENT COULD HAVE #
#                               #

# _get_content_size(self) method -> [width, height]
# if the element has a native size, like generated text, return it for autosizing purposes

# _scale(self) -> None
# if the element has needs to scale itself somehow, implement that here


class UI(ABC):
    def __init__(self, location, *args):
        self.visible = True

        self.location = location

        self.components = []
        self.add_components(*args)

        self.ui_scale = scale.get_scalar()
        self.user_scale = 1
        self.parent_user_scale = 1
        self.scale = 1
        self.system_scaling_enabled = True

        self._last_loop = -1

        # if unspecified width and height dimensions (represented as -1), tries to find a better solution
        self.size_sources = ["unset", "unset"]
        self.size_lastset = [-1, -1]
        self._auto_size()

    def _auto_size(self):
        self._auto_size_dimension(0)
        self._auto_size_dimension(1)
        self.size_lastset = [self.location.w, self.location.h]

    # dimension: 0 = width, 1 = height
    def _auto_size_dimension(self, dimension):
        content_dim = self._get_content_size()[dimension]

        if dimension == 0:
            set_location = "w"
            location_dim = self.location.w
        elif dimension == 1:
            set_location = "h"
            location_dim = self.location.h

        if location_dim == -1:
            if content_dim != -1:
                self.size_sources[dimension] = "element"
                setattr(self.location, set_location, content_dim / self.scale)

            elif self.components:
                child_loc = self.get_components()[0].location
                child_loc.resolve()  # pump the location to process if necessary
                child_dim = child_loc.get_resolved_base_rect()[2:4][dimension]
                if child_dim != -1:
                    self.size_sources[dimension] = "child"
                    setattr(
                        self.location,
                        set_location,
                        child_dim,
                    )
        else:
            self.size_sources[dimension] = "location"

    def _check_size(self):
        self._check_size_dimension(0)
        self._check_size_dimension(1)
        self.size_lastset = [self.location.w, self.location.h]

    # dimension: 0 = width, 1 = height
    def _check_size_dimension(self, dimension):
        if dimension == 0:
            set_location = "w"
            location_dim = self.location.w
        elif dimension == 1:
            set_location = "h"
            location_dim = self.location.h

        # if the location dimension is unset it tries to find a source to get a size
        if location_dim == -1:
            self._auto_size_dimension(dimension)

        elif self.size_sources[dimension] != "location":
            # priority escalation if it detects an outside change to the location object
            if self.size_lastset[dimension] != location_dim:
                self.size_sources[dimension] = "location"

            else:
                if self.size_sources[dimension] == "element":
                    content_dim = self._get_content_size()[dimension] / self.scale
                    # priority de-escalation if it can't find content size anymore
                    if content_dim == -1:
                        self.size_sources[dimension] = "child"
                    else:
                        setattr(self.location, set_location, content_dim)

                if self.size_sources[dimension] == "child":
                    if self.components:
                        child_dim = self.get_components()[
                            0
                        ].location.get_resolved_base_rect()[2:4][dimension]
                        setattr(self.location, set_location, child_dim)
                    # priority de-escalation again if it can't find a child size
                    else:
                        self.size_sources[dimension] = "unset"
                        setattr(self.location, set_location, -1)

    def display(self, screen=None, panel_dim=None):
        if not screen:
            screen = pygame.display.get_surface()

        # double display warning system
        if self._last_loop == time.get_loops():
            warnings.warn(
                f"{self.__class__.__name__} .display() seems to be called more than once per game loop",
                stacklevel=2,
            )
        self._last_loop = time.get_loops()

        # scaling system
        if self.system_scaling_enabled:
            self.ui_scale = scale.get_scalar()
        else:
            self.ui_scale = 1

        scalar = self.ui_scale * self.user_scale * self.parent_user_scale

        if self.scale != scalar:
            self.scale = scalar
            self._scale()  # process

        self.location.set_ui_scale(self.ui_scale)
        self.location.set_user_scale(self.user_scale * self.parent_user_scale)

        # dynamic sizing system
        self._check_size()

        # pygame.draw.rect(screen, (0, 0, 255), self.location.get_resolved_base_rect(), 1)

        if panel_dim != None:
            self.location.set_parent_context(panel_dim)

        if self.visible:
            self.location.resolve()  # drives the location to stay up to date with changes

            self._display(screen)

            for component in self.components:
                # custom scaling needs to filter down into sub-elements
                component.parent_user_scale = self.user_scale

                # we're testing this out
                component.parent = self

                # base_rect represents a newly resolved panel dimension
                # everything on this layer of abstraction is using unscaled numbers
                component.display(screen, self.location.get_resolved_base_rect())

    def copy(self):
        return copy.deepcopy(self)

    def _get_content_size(self):
        return [-1, -1]

    def add_component(self, *args):
        self.add_components(*args)

    def add_components(self, *args):
        args = list(args)

        for component in args:
            self.components.append(component)
            component.parent = self

    def get_components(self):
        return self.components

    def clear_components(self):
        self.components = []

    # should be overwritten by subclass
    def _scale(self):
        # print(f"{self.__class__} Does not know how to scale its content")
        pass

    # needs to be overwritten by subclass
    def _display(self, _):
        raise NotImplementedError("UI subclasses require an _display() method")

    """future:"""
    """Calling _scale or _display on a UI object that has not defined those with result in an exception being raised"""

    # public attributes
    # .location > pgx.Location object
    # .visible > boolean, controls whether object draws or not
    # .user_scale > individual scale of the element, automatically combined with global scale
    # .parent
    # .system_scaling_enabled
