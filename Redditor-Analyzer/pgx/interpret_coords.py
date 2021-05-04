from pgx.scale import scale


def interpret_coords(rect, align, panel_rect=False, ignore_offset=False):
    # if explicit area not passed in, use the screen dimensions as that area
    # different than 'if not panel_rect' b/c rects with zero size evaluate to false
    if panel_rect is False:
        panel_rect = [0, 0, *scale.get_resolution()]

    # defining constants for eval
    right = panel_rect[2]
    left = 0
    center = panel_rect[2] / 2
    top = 0
    bottom = panel_rect[3]
    width = panel_rect[2]
    height = panel_rect[3]

    # change rect location to where it should be, pixel wise
    # also evaluates any text used to define locations
    for i in range(len(rect)):
        t = type(rect[i])
        if t == str:
            rect[i] = eval(rect[i])
        elif t == int or t == float:
            pass
        else:
            raise TypeError("coordinates can be in strings, ints, or floats only")

    rect[0] += panel_rect[0]
    rect[1] += panel_rect[1]

    # further alignment
    if align == "left":
        pass
    elif align == "right":
        rect[0] -= rect[2]
    elif align == "center":
        rect[0] -= rect[2] / 2
    else:
        raise ValueError("align can be: 'left', 'right', or 'center' only")

    # global offsets
    if not ignore_offset:
        rect[0] += scale.get_offset()[0]
        rect[1] += scale.get_offset()[1]
