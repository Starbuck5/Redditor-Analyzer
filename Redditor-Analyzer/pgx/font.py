import math
import string

import pygame

from pgx import image
from pgx import path


class font:
    @staticmethod
    def _init():
        pygame.freetype.init()

        # enum font stuffs
        font.opensans = font._load_font("opensans")
        font.lato = font._load_font("lato")
        font.montserrat = font._load_font("montserrat")
        font.roboto = font._load_font("roboto")
        font.robotocondensed = font._load_font("robotocondensed")
        font.sourcesanspro = font._load_font("sourcesanspro")
        font.fixedsys = font._load_font("fixedsys")
        font.classic = font._create_font_classic()

    def _load_font(name):
        return font.Font(path.handle(f"fonts/{name}/{name}.ttf", True))

    @staticmethod
    def _create_font_classic():
        char_index = list(
            "!\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`{|}~"
        )
        font_sheet = pygame.image.load(path.handle("fonts\\classic\\font.bmp", True))
        char_list = image.break_sprite(font_sheet, 8, 13, 2, 2, 4, 17)
        char_image = dict(zip(char_index, char_list))

        # creating lowercase letters
        # in this font capitals and lowercase are represented by the same images
        for char in string.ascii_uppercase:
            char_image[char.lower()] = char_image[char]

        # adding in the space
        char_image[" "] = pygame.Surface((8, 13), pygame.SRCALPHA)

        # color correction
        # the font image is stored as a 1 bit format, no transparency, only black or white
        for char in char_image:
            char_image[char].set_colorkey((255, 255, 255))

        # creating half sizers
        # manually setting some of the characters to have the explicit px width of 4,
        # not their image width of 8
        for char in list("!'*,.:;`|"):
            char_image[char] = (char_image[char], 4)

        return font.CustomFont(char_image, 15, (0, 0, 0), 2)

    class Font:
        def __init__(self, filepath):
            self.path = path.handle(filepath)
            self.Font = pygame.freetype.Font(self.path)

            # used by get_metrics(), which requires setting attributes
            # directly on the font, rather than passing them in like render()
            self.dummy_font = pygame.freetype.Font(self.path)

        # returns a tuple (image, rect)
        def render(self, textstr, size, bgcolor, color, style):
            calc_size = self.Font.get_rect(textstr, size=size, style=style)

            y = size - calc_size.y + self.Font.get_sized_descender(size)

            ydiff = 0
            if y < 0:
                ydiff = -y
                y = 0

            surf = pygame.Surface(
                (calc_size.w if calc_size.w != 0 else 1, size + ydiff), pygame.SRCALPHA
            )

            # render_to() returns a rect, but that rect is not used.
            self.Font.render_to(
                surf,
                (
                    0,
                    y,
                ),
                textstr,
                fgcolor=color,
                bgcolor=bgcolor,
                size=size,
                style=style,
            )

            return surf, surf.get_rect()

        def get_metrics(self, textstr, size, style):
            self.dummy_font.style = style

            m = self.dummy_font.get_metrics(textstr, size)

            # patch trailing whitespace not being appreciated
            if textstr and textstr[-1] == " ":
                m[-1] = (m[-1][0], m[-1][4], m[-1][2], m[-1][3], m[-1][4], m[-1][5])

            # if the textstr contains characters that the font can't render, it puts a None in
            # as the metric for that character.
            # This bit of code replaces unknown characters with the unicode for 'unknown character'
            # which, ironically, is a known character and can give a valid metric.
            if any([metric is None for metric in m]):
                textstr = "".join(
                    [
                        "\FFF0" if metric is None else textstr[i]
                        for i, metric in enumerate(m)
                    ]
                )
                m = self.dummy_font.get_metrics(textstr, size)

            if m:
                prev_x = -m[0][0]

                for i, metric in enumerate(m):
                    m[i] = (
                        prev_x + metric[0],
                        prev_x + metric[1],
                        0,
                        size,
                        metric[4],
                        metric[5],
                    )
                    prev_x += m[i][4]

            return m

        def find_px_length(self, textstr, size, style):
            return self.Font.get_rect(textstr, size=size, style=style).w

        # for some reason freetype font instances can't be automatically copied with copy.deepcopy()
        # this is my mitigation
        def copy(self):
            return self.__class__(self.path)

        def __copy__(self):
            return self.copy()

        def __deepcopy__(self, memo):
            return self.copy()

        def __str__(self):
            return f"pgx.font.Font: {self.Font.name}"

    # class that allows you to create pixelart fonts from images relatively easy
    class CustomFont(Font):
        # char_images = {"char": pygame.Surface, "char": (pygame.Surface, custom width)}
        # current_size = the current height of the font in pixels.
        # gap = the gap between characters in pixels, at the current_size
        def __init__(self, char_images, current_size, current_color, gap):
            self.char_images = char_images
            self.image_size = current_size
            self.image_color = current_color
            self.gap = gap

        # the meat of the __init__, automatically called on demand b/c pgx.init comes before
        # video init so can't do surface operations.
        def _setup(self):
            if "missing" not in self.char_images:
                h = self.image_size

                w = int(self.image_size / 2)
                w = 1 if w < 1 else w

                line_width = int(self.image_size / 6)
                line_width = 1 if line_width < 1 else line_width

                surf = pygame.Surface((w, h), pygame.SRCALPHA)
                pygame.draw.rect(
                    surf, self.image_color, [0, 0, w - line_width / 2, h], line_width
                )
                self.char_images["missing"] = surf

            for char in self.char_images:
                im = self.char_images[char]
                try:
                    im[1]
                    self.char_images[char] = (im[0].convert_alpha(), im[1])
                except:
                    self.char_images[char] = (im.convert_alpha(), im.get_width())

            self.cached = (self.image_size, self.char_images.copy(), self.gap)

        # returns a tuple (image, rect)
        def render(self, textstr, size, bgcolor, color, style):
            width = self.find_px_length(textstr, size, style)
            width = math.ceil(width)
            surf = pygame.Surface((width if width != 0 else 1, size), pygame.SRCALPHA)
            surf.fill(bgcolor)

            _, font_chars, gap = self.cached
            text = self._process_text(textstr)

            x = 0
            for char in text:
                # turning the scaled character image to the right color
                char_im = pygame.PixelArray(font_chars[char][0].copy())
                char_im.replace(self.image_color, color)
                char_im = char_im.make_surface()

                surf.blit(char_im, (x, 0))
                x += font_chars[char][1] + gap

            return surf, surf.get_rect()

        def get_metrics(self, textstr, size, style):
            # (min_x, max_x, min_y, max_y, horizontal_advance_x, horizontal_advance_y)
            # only imitates what is used later on (for now)

            if self.cached[0] != size:
                self._resize_images(size)

            _, font_chars, gap = self.cached
            text = self._process_text(textstr)

            metrics = []

            prev_x = 0
            for char in text:
                char_width = font_chars[char][1]
                metrics.append(
                    (prev_x, prev_x + char_width, 0, size, char_width + gap, -1)
                )
                prev_x += char_width + gap

            return metrics

        # part of the common font standard
        def find_px_length(self, textstr, size, style):
            if not getattr(self, "cached", False):
                self._setup()

            if textstr == "":
                return 0

            if self.cached[0] != size:
                self._resize_images(size)

            _, font_chars, gap = self.cached
            text = self._process_text(textstr)

            length = font_chars[text.pop(0)][1]
            for char in text:
                length += gap + font_chars[char][1]

            return length

        # scales all of the character images and puts them in a place to be accessed
        def _resize_images(self, size):
            scalar = size / self.image_size

            scaled_images = {}
            for char in self.char_images:
                im = image.scale(self.char_images[char][0], scalar)
                width = self.char_images[char][1] * scalar
                scaled_images[char] = (im, width)

            self.cached = (size, scaled_images, self.gap * scalar)

        # takes a string, returns char list. any characters not in font are told to use "missing"
        def _process_text(self, textstr):
            text = list(textstr)
            for i, char in enumerate(text):
                if char not in self.char_images:
                    text[i] = "missing"

            return text

        def copy(self):
            return self.__class__(
                self.char_images, self.image_size, self.image_color, self.gap
            )
