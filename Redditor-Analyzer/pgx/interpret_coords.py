from pgx.data import data


def interpret_coords(rect, align, panel_rect=False, ignore_offset=False):
    # if explicit area not passed in, use the screen dimensions as that area
    if not panel_rect:
        panel_rect = [0, 0, *data.get_resolution()]

    # defining constants for eval
    right = panel_rect[0] + panel_rect[2]
    left = panel_rect[0]
    center = panel_rect[0] + panel_rect[2] / 2
    top = panel_rect[1]
    bottom = panel_rect[1] + panel_rect[3]
    width = panel_rect[2]
    height = panel_rect[3]

    # change rect location to where it should be, pixel wise
    # also evaluates any text used to define locations
    for i in range(len(rect)):
        if isinstance(rect[i], str):
            rect[i] = eval(rect[i])
        elif isinstance(rect[i], int) or isinstance(rect[i], float):
            if i < 2:
                rect[i] += panel_rect[i]
        else:
            raise TypeError("coordinates can be in strings or in ints only")

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
        rect[0] += data.get_global_offset()[0]
        rect[1] += data.get_global_offset()[1]
