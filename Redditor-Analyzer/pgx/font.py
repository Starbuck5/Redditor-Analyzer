import pygame
import pygame.freetype
from pgx.image import image
from pgx.handle_path import handle_path


class font:
    @staticmethod
    def init():
        pygame.freetype.init()
        font_folder = "fonts"

        # enum font stuffs
        font.classic = font._CustomFont(f"{font_folder}\\classic\\font.gif")
        font.opensans = font._InternalFont(f"{font_folder}\\opensans\\opensans.ttf")
        font.lato = font._InternalFont(f"{font_folder}\\lato\\lato.ttf")
        font.montserrat = font._InternalFont(
            f"{font_folder}\\montserrat\\montserrat.ttf"
        )
        font.roboto = font._InternalFont(f"{font_folder}\\roboto\\roboto.ttf")
        font.robotocondensed = font._InternalFont(
            f"{font_folder}\\robotocondensed\\robotocondensed.ttf"
        )
        font.sourcesanspro = font._InternalFont(
            f"{font_folder}\\sourcesanspro\\sourcesanspro.ttf"
        )

    class Font:
        def __init__(self, path):
            self.path = handle_path(path)
            self.Font = pygame.freetype.Font(self.path)

        # returns a tuple (image, rect)
        def render(self, textobj):
            size = self.Font.get_rect(
                textobj.text, size=textobj.size, style=textobj.style
            )

            surf = pygame.Surface(
                (size.w if size.w != 0 else 1, textobj.size), pygame.SRCALPHA
            )
            surf.fill((0, 0, 0, 0))

            rect = self.Font.render_to(
                surf,
                (
                    0,
                    textobj.size - size.y + self.Font.get_sized_descender(textobj.size),
                ),
                textobj.text,
                fgcolor=textobj.color,
                bgcolor=textobj.bgcolor,
                size=textobj.size,
                style=textobj.style,
            )

            return surf, surf.get_rect()

        # for some reason freetype font instances can't be automatically copied with copy.deepcopy()
        # this is my mitigation
        def copy(self):
            return pygame.freetype.Font(self.path)

        def __copy__(self):
            return self.copy()

        def __deepcopy__(self, memo):
            return self.copy()

        def __str__(self):
            return f"pgx.font.Font: {self.Font.name}"

    # loads the font resource from internal pgx resources
    class _InternalFont(Font):
        def __init__(self, path):
            self.path = handle_path(path, True)
            self.Font = pygame.freetype.Font(self.path)

    """
    Issue with ending with !
    Looks real small
    Could be like that all the time, idk
    """

    class _CustomFont:
        def __init__(self, path):
            self.missingTexture = self._makeMissingTexture()
            self.char_index = list(
                "0123456789abcdefghijklmnopqrstuvwxyz:,[]?+%|-&.'!/()_"
            )
            self.font_sheet = pygame.image.load(handle_path(path, True))
            self.char_list = image.break_sprite(
                self.font_sheet, 8, 13, 2, 1, 6, [10, 10, 10, 6, 10, 7]
            )
            self.half_size = ["'", ".", ":" ",", "!", "|"]

        def _makeMissingTexture(self):
            missingTexture = pygame.Surface((8, 12))
            for i in range(6):
                x = 2 if i % 2 == 0 else 0
                pygame.draw.rect(missingTexture, (255, 0, 220), (x, i * 2, 2, 2), 0)
                pygame.draw.rect(missingTexture, (255, 0, 220), (x + 4, i * 2, 2, 2), 0)
            return missingTexture

        def render(self, textobj):
            # explicitly pulled out so it can be scaled to be in line with other fonts
            size = textobj.size
            size /= 16

            string = textobj.text
            string = string.lower()

            # creates a surface to draw the text onto
            surf = pygame.Surface(
                (self._textlength(size, string), self._textheight(size, string))
            )
            surf = surf.convert_alpha()
            surf.fill(textobj.bgcolor)

            length = 0
            padding = 3
            for i in range(len(string)):
                # drawing
                char_image = False
                if string[i] in self.char_index:
                    char_image = self.char_list[self.char_index.index(string[i])]
                    char_image.set_palette_at(
                        0, textobj.color
                    )  # sets the letters to the right color
                    char_image = char_image.convert_alpha()
                elif string[i] == " ":
                    pass
                else:
                    char_image = self.missingTexture

                if char_image:
                    surf.blit(image.scale(char_image, size), (length, 0))

                # calculating next position
                if i == len(string) - 1:
                    padding = 0
                if string[i] != " " and not string[i] in self.half_size:
                    length += (8 + padding) * size
                elif string[i] in self.half_size:
                    length += (2 + padding) * size
                elif string[i] == " " and string[i - 1] != " " and i != 0:
                    length += (3 + padding) * size
                elif string[i] == " " and string[i - 1] == " " and i != 0:
                    length += (8 + padding) * size

            # surf = surf.convert_alpha()
            return (surf, surf.get_rect())

        def _textlength(self, size, string):
            length = 0
            padding = 3
            for i in range(len(string)):
                if i == len(string) - 1:
                    padding = 0
                if string[i] != " " and not string[i] in self.half_size:
                    length += (8 + padding) * size
                elif string[i] in self.half_size:
                    length += (2 + padding) * size
                elif string[i] == " " and string[i - 1] != " " and i != 0:
                    length += (3 + padding) * size
                elif string[i] == " " and string[i - 1] == " " and i != 0:
                    length += (8 + padding) * size
            return length

        # really a pretty lame function b/c font doesn't support newlines
        def _textheight(self, size, string):
            return size * 12
