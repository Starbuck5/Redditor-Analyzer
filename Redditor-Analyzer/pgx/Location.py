import pygame

from pgx.interpret_coords import interpret_coords

from pgx.data import data

"""
I suppose you should consider caching resolve and using setattr again

It could use multiple arg support -- "top-bottom+10-37+height" #likely not that elaborate but it could be helpful
"""

"""

NEEDS SERIOUS WORK

the interface for accessing various locations (real? fake? offsets/anchors?) is unclear

the interface for moving is nonexistent

the weird back compat with rect should be removed

consider stealing pygame rect api for things

"""


class Location:
    # implementation deets:
    # self.rect is the permanent offset storage, editable
    # self.rect_anchors is the permanent anchor storage
    # self._rect is reconstituted from other rect stuff on demand, then returned

    # init styles
    # Location([230, 40, 10, 20], "center")
    # Location(["center", "top", "width/2", "height"])
    # Location([0,0]) = Location([0,0,0,0])
    # Location() = Location([0,0,0,0])

    # __init__(self, rect, align="left") #parameters
    # rect can be [x,y,w,h], [x,y] or pygame.Rect
    def __init__(self, *args):
        # processing alternative forms of init
        if len(args) == 0:
            rect = [0, 0, 0, 0]
            align = "left"
        elif len(args) == 1:
            rect = args[0]
            align = "left"
        elif len(args) == 2:
            rect, align = args
        else:
            raise TypeError(
                "Location takes 0-2 parameters but {len(args)} parameters were given"
            )

        rect = list(rect)
        try:
            if len(rect) == 2:
                rect += [0, 0]
        except:
            raise TypeError("Location rect arg must be a list-esque thing (a sequence)")

        # actually initializing
        self.__dict__["scale"] = 1
        self.align = align

        self.base_panel_dim = [0, 0, *data.get_resolution()]
        self.real_panel_dim = self.base_panel_dim.copy()

        self.base_offsets, self.anchors = self._split_format_rect(rect)
        self.real_offsets = self.base_offsets.copy()

        self.current_rect = -1
        self._resolve()

        self.last_offset = [0, 0]

    # breaks rect ['20', 'right-12', 77, 'top-10'] into numbers and anchors
    def _split_format_rect(self, rect):
        rect_anchors = [0, 0, 0, 0]
        anchors = ["center", "right", "left", "top", "bottom", "width", "height"]
        center, right, left, top, bottom, width, height = [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]  # variables set to zero for eval
        for i in range(len(rect)):
            if isinstance(rect[i], str):
                for anchor in anchors:
                    if anchor in rect[i]:
                        rect_anchors[i] = anchor
                        break

                # what does this accomplish?
                if not rect_anchors[i]:
                    raise ValueError(f"Location cannot process '{rect[i]}'")

                rect[i] = eval(rect[i])  # gets rid of string bits

        return rect, rect_anchors

    def _scale_numlist(self, numlist):
        numlist = list(numlist)  # .copy() that also casts to list
        for i in range(len(numlist)):
            numlist[i] *= self.scale
        return numlist

    def _scale(self):
        self.real_offsets = self._scale_numlist(self.base_offsets)
        self.real_panel_dim = self._scale_numlist(self.base_panel_dim)

    def _resolve(self):
        # creating current_rect
        new_real = list(self.real_offsets)  # .copy() that also casts to list
        for i, (offset, anchor) in enumerate(zip(self.real_offsets, self.anchors)):
            if anchor:
                new_real[i] = anchor + "+" + str(offset)

        interpret_coords(new_real, self.align, self.real_panel_dim)
        self.current_rect = pygame.Rect(new_real)

        # creating base_rect, used by UI scaling to have something firm to grab on to
        # see pgx.ui.UI.display()
        new_base = self.base_offsets.copy()
        for i, (offset, anchor) in enumerate(zip(self.base_offsets, self.anchors)):
            if anchor:
                new_base[i] = anchor + "+" + str(offset)

        interpret_coords(new_base, self.align, self.base_panel_dim, True)
        self.base_rect = pygame.Rect(new_base)

    def resolve(self):
        # diff approach than other 'dynamic resizing' stuff
        # just checks every tick, rather than checking for setattr changes
        if self.last_offset != data.get_global_offset():
            self.last_offset = data.get_global_offset()
            self._resolve()

        return self.current_rect

    def __str__(self):
        return f"Location at {self.current_rect}"

    def get_align(self):
        return self.align

    def set_align(self, align):
        self.align = align

    """
    probably needs some behavior for set rect
    """

    def __setattr__(self, name, value):
        if name == "scale" and value != self.scale:
            self.__dict__["scale"] = value
            self._scale()
            self._resolve()
        elif name == "panel_dim" and value and value != self.base_panel_dim:
            self.__dict__["base_panel_dim"] = value
            self._scale()
            self._resolve()
        elif name == "rect":
            self.__dict__["base_offsets"] = list(value)
            self._scale()
            self._resolve()
        else:
            self.__dict__[name] = value

    def __getattr__(self, name):
        if name == "rect":
            return pygame.Rect(self.__dict__["base_offsets"])
        return self.__dict__[name]

    # IS this even true?
    """     
    #public attribute
    #.rect
    #can be used for all those fun pygame.Rect operations
    """
