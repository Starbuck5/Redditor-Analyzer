import pygame

from pgx.handle_path import handle_path

# a bundle of methods for loading and operating on surfaces
# all size methods will accept float dimension input, it is rounded
class image:
    # loads from file, returns image, optional scale argument
    @staticmethod
    def load(path):
        handle_path(path)
        return pygame.image.load(handle_path(path))

    # scales an image by a scalar
    @staticmethod
    def scale(pic, scalar):
        x = pic.get_width() * scalar
        x = round(x) if x > 0 else 1
        y = pic.get_height() * scalar
        y = round(y) if y > 0 else 1
        return pygame.transform.scale(pic, (x, y))

    # scales image to the size given, regardless of aspect ratio or aesthetics
    @staticmethod
    def stretch(pic, size):
        pic = pygame.transform.scale(pic, (round(size[0]), round(size[1])))
        return pic

    # a version of scretch that preserves aspect ratio by using black bars if necessary
    @staticmethod
    def fit(pic, size, bg_color=False):
        returnImage = pygame.Surface(size)

        if bg_color:
            returnImage = returnImage.convert_alpha()
            returnImage.fill(bg_color)

        scale = 1 / max(pic.get_width() / size[0], pic.get_height() / size[1])
        pic = image.scale(pic, scale)
        if pic.get_width() == size[0]:
            returnImage.blit(pic, (0, (size[1] - pic.get_height()) / 2))
        elif pic.get_height() == size[1]:
            returnImage.blit(pic, ((size[0] - pic.get_width()) / 2, 0))
        else:
            raise RuntimeError("it seems fitImage was unable to scale the image :(")
        return returnImage

    # pixelart image rotater, scales it up and down again to preserve detail
    @staticmethod
    def pixel_rotate(pic, degrees):
        pic = image.scale(pic, 4)
        pic = pygame.transform.rotate(pic, degrees)
        pic = image.scale(pic, 0.25)
        return pic

    """
    needs more improvement than anything else in image module 
    """
    # quite difficult method to break up sprite sheets into rectangular components
    #'width' and 'height' refer to the dimensions of each outputted surface
    #'margin' and 'vertmargin' refer to space between each desired rect subsection on the horizontal and vertical axis
    #'rows' and 'columns' refer to the amount of rectangles there are to pick out
    #'columns' can be a list, if multiple numbers of columns exist on separate rows
    @staticmethod
    def break_sprite(sheet, width, height, margin, vertmargin, rows, columns):
        if not isinstance(columns, list):
            relcolumns = []
            for i in range(rows):
                relcolumns.append(columns)
            columns = relcolumns
        if len(columns) != rows:
            raise Exception("column and row mismatch")

        image_list = []
        for i in range(rows):
            for j in range(columns[i]):
                rect = ((width + margin) * j, (height + vertmargin) * i, width, height)
                try:
                    image_list.append(sheet.subsurface(rect))
                except ValueError:
                    raise ValueError(
                        f"sheet area {rect} is out of range of the supplied image"
                    )
        return image_list

    # takes a picture and an rgba, applies that rgba to the picture, basically putting a transparent film in front of the
    # image, with the transparency regulated by the 'a' of rgba
    # rgba can be a list, a tuple, or a pygame.Color
    @staticmethod
    def obscure(pic, color):
        if len(color) != 4:
            raise ValueError("image.obscure needs an rgba, not just an rgb")
        r, g, b, a = color

        overlay = pygame.Surface(pic.get_size())
        overlay.fill((r, g, b))
        overlay.set_alpha(a)

        pic.blit(overlay, (0, 0))
        return pic
