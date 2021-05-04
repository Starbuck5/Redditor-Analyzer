import copy
import string
from typing import Union

import pygame.freetype

from pgx.font import font


class Text:
    # ------------------------------------------------------------------------------------------#
    #                                  STATIC CLASS FEATURES                                    #
    # ------------------------------------------------------------------------------------------#

    # change any of the defaults by accessing their attributes
    default_color = (0, 0, 0, 255)
    default_bgcolor = (0, 0, 0, 0)
    default_font = None
    default_style = pygame.freetype.STYLE_DEFAULT
    default_align = "left"
    default_spacing = 1.5

    @staticmethod
    def _init():
        Text.default_font = font.opensans

    # ------------------------------------------------------------------------------------------#
    #                                         ATTRIBUTES                                        #
    # ------------------------------------------------------------------------------------------#

    __slots__ = (
        [
            "_text",
            "_size",
            "_font",
            "_color",
            "_bgcolor",
            "_style",
            "_align",
            "_spacing",
            "_limit",
        ]
        + [
            "image",
            "rect",
            "metrics",
            "metrics_byline",
            "rect_metrics",
            "rect_metrics_byline",
        ]
        + ["_changed"]
    )

    def set_text(self, textstr: str) -> None:
        if not isinstance(textstr, str):
            raise TypeError("text must be a string")

        if getattr(self, "_text", None) != textstr:
            self._changed = True
            self._text = textstr

    def set_size(self, size: Union[int, float]) -> None:
        try:
            size + 1
        except:
            raise TypeError("size must be a number")

        if getattr(self, "_size", None) != size:
            self._changed = True
            self._size = size

    def set_font(self, font) -> None:
        if getattr(self, "_font", None) != font:
            self._changed = True
            self._font = font

    def set_color(self, color) -> None:
        if getattr(self, "_color", None) != color:
            self._changed = True
            self._color = color

    def set_bgcolor(self, bgcolor) -> None:
        if getattr(self, "_bgcolor", None) != bgcolor:
            self._changed = True
            self._bgcolor = bgcolor

    def set_style(self, style: int) -> None:
        if getattr(self, "_style", None) != style:
            self._changed = True
            self._style = style

    ALIGNMENTS = {"left", "right", "center"}

    def set_align(self, align: str) -> None:
        if not isinstance(align, str):
            raise TypeError(f"align value must be a string in {self.alignments}")

        if not align in self.ALIGNMENTS:
            raise ValueError(f"align value must be in {self.alignments}")

        if getattr(self, "_align", None) != align:
            self._changed = True
            self._align = align

    def set_spacing(self, spacing: Union[int, float]) -> None:
        if getattr(self, "_spacing", None) != spacing:
            self._changed = True
            self._spacing = spacing

    def set_limit(self, limit: Union[int, float, bool]) -> None:
        if limit < 0:
            limit = 0

        if getattr(self, "_limit", None) != limit:
            self._changed = True
            self._limit = limit

    def make_getter(name):
        return lambda x: getattr(x, f"_{name}")

    text = property(make_getter("text"), set_text)
    size = property(make_getter("size"), set_size)
    font = property(make_getter("font"), set_font)
    color = property(make_getter("color"), set_color)
    bgcolor = property(make_getter("bgcolor"), set_bgcolor)
    style = property(make_getter("style"), set_style)
    align = property(make_getter("align"), set_align)
    spacing = property(make_getter("spacing"), set_spacing)
    limit = property(make_getter("limit"), set_limit)

    # ------------------------------------------------------------------------------------------#
    #                                         FUNCTIONS                                         #
    # ------------------------------------------------------------------------------------------#

    def __init__(self, textstr, size, **kwargs):
        self.text = textstr
        self.size = size
        self.limit = False

        self._set_property("font", kwargs)
        self._set_property("color", kwargs)
        self._set_property("bgcolor", kwargs)
        self._set_property("style", kwargs)
        self._set_property("align", kwargs)
        self._set_property("spacing", kwargs)

        self._changed = True

    def _set_property(self, name, kwargs):
        setattr(
            self,
            name,
            getattr(Text, f"default_{name}") if name not in kwargs else kwargs[name],
        )

    def get_rect(self) -> pygame.Rect:
        """Returns a rect from the text, rerenders the text if necessary."""
        if self._changed:
            self._generate()
            self._changed = False
        return self.rect

    def get_image(self) -> pygame.Surface:
        """Returns an image of the text, rerendering if necessary."""
        if self._changed:
            self._generate()
            self._changed = False
        return self.image

    def get_metrics(self) -> list:
        if self._changed:
            self._generate()
            self._changed = False
        return self.metrics

    def get_metrics_lines(self) -> list:
        if self._changed:
            self._generate()
            self._changed = False
        return self.metrics_byline

    def get_rect_metrics(self) -> list:
        if self._changed:
            self._generate()
            self._changed = False
        return self.rect_metrics

    def get_rect_metrics_byline(self) -> list:
        if self._changed:
            self._generate()
            self._changed = False
        return self.rect_metrics_byline

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f"pgx.Text: '{self.text}'"

    def copy(self):
        return copy.copy(self)

    # ------------------------------------------------------------------------------------------#
    #                                       TEXT GENERATION                                     #
    # ------------------------------------------------------------------------------------------#

    WHITESPACE = set(string.whitespace)

    # splits text into a list of words
    # in runs of whitespace, each char counts as its own word
    def _split_words(self):
        words = []
        text = self.text
        lastcut = 0
        for i in range(1, len(text)):
            char = text[i]
            lastchar = text[i - 1]

            if char in self.WHITESPACE or lastchar in self.WHITESPACE:
                words.append(text[lastcut:i])
                lastcut = i

        words.append(text[lastcut:])

        return words

    # splits text into a list of lines, applying the limit setting
    def _split_lines(self):
        words = self._split_words()

        lines = []
        current_line = ""
        while words:
            if words[0] == "\n":
                lines.append(current_line)
                current_line = ""
                del words[0]

            else:
                l = self.font.find_px_length(
                    current_line + words[0], self.size, self.style
                )

                # if adding this word goes over the limit...
                if self.limit is not False and l > self.limit:

                    # if one word is longer than the limit on its own
                    if current_line == "":

                        # if the word making it go over is a single character
                        if len(words[0]) == 1:
                            current_line += words.pop(0)

                        # otherwise atomize the current word into characters
                        else:
                            words[0:1] = list(words[0])

                    # normal case
                    else:
                        lines.append(current_line)
                        current_line = ""

                # if there is still more room for words on this line
                else:
                    current_line += words.pop(0)

        if current_line:
            lines.append(current_line)

        return lines

    def _generate(self):
        # empty strings
        if self.text == "":
            self.image, self.rect = self.font.render(
                "", self.size, self.bgcolor, self.color, self.style
            )
            self.metrics = None
            self.metrics_byline = None
            self.rect_metrics = None
            self.rect_metrics_byline = None
            return

        images = []
        rects = []
        metrics = []
        metrics_byline = []
        rect_metrics = []
        rect_metrics_byline = []

        for line in self._split_lines():
            image, rect = self.font.render(
                line, self.size, self.bgcolor, self.color, self.style
            )

            # fixes the line rects as per the spacing setting
            if rects:
                rects[-1].h *= self.spacing
                rect.y = rects[-1].bottom

            line_metrics = self.font.get_metrics(line, self.size, self.style)

            rects.append(rect)
            images.append(image)
            metrics_byline.append(line_metrics)
            rect_metrics_byline.append([])

        # creating overall rectangle out of the line rectangles
        self.rect = rects[0].unionall(rects[1:])
        if self.limit is not False:
            self.rect.w = self.limit

        # makes selectability on the final line look good
        # just trust me
        if len(rects) > 1:
            rects[-1].h *= self.spacing

        # aligning the metrics
        for i in range(len(metrics_byline)):
            # fixes the line rects as per the align setting
            rect = rects[i]
            if self.align == "right":
                rect.x = self.rect.w - rect.w
            elif self.align == "center":
                rect.x = self.rect.w / 2 - rect.w / 2

            # fixes the metrics to the line rects
            line_metrics = metrics_byline[i]
            for j, metric in enumerate(line_metrics):
                metric = (
                    metric[0] + rect.x,
                    metric[1] + rect.x,
                    rect.top,
                    rect.bottom,
                    metric[4],
                    metric[5],
                )

                metrics.append(metric)
                line_metrics[j] = metric

                # creates a rect version of the metrics
                rect_metric = pygame.Rect(
                    metric[0], metric[2], metric[1] - metric[0], metric[3] - metric[2]
                )
                rect_metrics.append(rect_metric)
                rect_metrics_byline[i].append(rect_metric)

                # sets the last rect to come right up to the current rect
                try:
                    lm = rect_metrics_byline[i][-2]
                    lm.width = rect_metric.x - lm.x
                except IndexError:
                    pass

        self.metrics = metrics
        self.metrics_byline = metrics_byline
        self.rect_metrics = rect_metrics
        self.rect_metrics_byline = rect_metrics_byline

        # uses the area to create a surface to store everything on
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)

        # places all of the images into their correct locations
        for rect, image in zip(rects, images):
            surf.blit(image, rect)
        self.image = surf

    # public attributes:
    # .text
    # .size
    # .font
    # .color
    # .bgcolor
    # .style
    # .align
    # .spacing
    # .limit
    # modifying any of these attributes calls the _generate function again, changing the text object contents


# compat
LinedText = Text
