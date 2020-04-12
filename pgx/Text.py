from pgx.font import font
import copy


class Text:
    default_color = ""
    default_bgcolor = ""
    default_font = ""

    @staticmethod
    def init():
        # actual setup
        Text.default_color = (0, 0, 0, 255)
        Text.default_bgcolor = (0, 0, 0, 0)
        Text.default_font = font.opensans

    # change any of the defaults by accessing their attributes

    # kwargs:
    # bgcolor (background color)
    # color (actual text color)
    # font (sets font, input pgx.font.font_name (it's an enum-esque thing))
    """
    #           I want this kwarg but I haven't been able to get it to work
    #           style - pygame.freetype.constant - see pygame.org/docs/ref/freetype.html#pygame.freetype.Font.style
    """

    def __init__(self, textstr, size, **kwargs):
        self.__dict__["color"] = (
            Text.default_color if "color" not in kwargs else kwargs["color"]
        )
        self.__dict__["bgcolor"] = (
            Text.default_bgcolor if "bgcolor" not in kwargs else kwargs["bgcolor"]
        )
        self.__dict__["font"] = (
            Text.default_font if "font" not in kwargs else kwargs["font"]
        )

        self.__dict__["size"] = size
        self.__dict__["text"] = textstr

        self._generate()

    # create the actual text image from settings
    def _generate(self):
        image_plus_rect = self.font.render(self)
        self.__dict__["rect"] = image_plus_rect[1]
        self.__dict__["image"] = image_plus_rect[0].convert_alpha()

    def get_rect(self):
        return self.rect

    def get_image(self):
        return self.image

    def __setattr__(self, name, value):
        oldval = None if name not in self.__dict__ else self.__dict__[name]
        self.__dict__[name] = value
        # only regenerates if a new value was actually set and it was a pre-existing value (ie, relevant)
        if oldval != value and oldval != None:
            self._generate()

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return f"pgx.Text: '{self.text}'"

    def copy(self):
        return copy.copy(self)

    # public attributes:
    # .text
    # .font
    # .size
    # .bgcolor
    # .color
    # modifying any of these attributes calls the _generate function again, changing the text object contents
