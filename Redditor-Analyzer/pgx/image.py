import pygame

from pgx import path

# a bundle of methods for loading and operating on surfaces
# all size methods will accept float dimension input, it is rounded

# loads from file, returns image, optional scale argument
def load(filepath):
    return pygame.image.load(path.handle(filepath))


# scales an image by a scalar
def scale(pic, scalar):
    x = pic.get_width() * scalar
    x = round(x) if x > 0 else 1
    y = pic.get_height() * scalar
    y = round(y) if y > 0 else 1
    return pygame.transform.scale(pic, (x, y))


# scales image to the size given, regardless of aspect ratio or aesthetics
def stretch(pic, size):
    pic = pygame.transform.scale(pic, (round(size[0]), round(size[1])))
    return pic


# a version of scretch that preserves aspect ratio by using black bars if necessary
def fit(pic, size, bg_color=False):
    return_im = pygame.Surface(size)

    if bg_color:
        return_im = return_im.convert_alpha()
        return_im.fill(bg_color)

    new_rect = pic.get_rect().fit(pygame.Rect(0, 0, *size))
    pic = pygame.transform.scale(pic, (new_rect.w, new_rect.h))
    return_im.blit(pic, new_rect)

    return return_im


# pixelart image rotater, scales it up and down again to preserve detail
def pixel_rotate(pic, degrees):
    pic = scale(pic, 4)
    pic = pygame.transform.rotate(pic, degrees)
    pic = scale(pic, 0.25)
    return pic


"""
needs more improvement than anything else in image module 
"""
# quite difficult method to break up sprite sheets into rectangular components
#'width' and 'height' refer to the dimensions of each outputted surface
#'margin' and 'vertmargin' refer to space between each desired rect subsection on the horizontal and vertical axis
#'rows' and 'columns' refer to the amount of rectangles there are to pick out
#'columns' can be a list, if multiple numbers of columns exist on separate rows
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


# rgba can be a list, a tuple, or a pygame.Color
def obscure(pic, color, area=None):
    """Overlay the rgba color onto the whole Surface, or a specific area"""
    if len(color) != 4:
        raise ValueError("image.obscure needs an rgba, not just an rgb")
    r, g, b, a = color

    if area is None:
        area = pic.get_rect()
    else:
        area = pygame.Rect(area)

    overlay = pygame.Surface(area.size)
    overlay.fill((r, g, b))
    overlay.set_alpha(a)

    pic.blit(overlay, area)
