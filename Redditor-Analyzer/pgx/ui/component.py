import pygame

from pgx.events import events
from pgx.Location import Location
from pgx.key import key
from pgx import image
from pgx._scrap import scrap

from pgx.ui.UI import UI

__all__ = ["Selectable"]


class Selectable(UI):
    ALLOWED_PARENTS = (
        "TextBox",
        "InputBox",
    )  # changed into actual classes in __init__.py

    def __init__(self, color=(0, 25, 220, 80)):
        self.select_color = color

        super().__init__(Location())

        self.down_at = False
        self.up_at = False
        self.indices_state = False
        self.relevant_text = ""

        self.set_bounds_ = False

        self.setup = False

        if not scrap.get_init():
            scrap.init()

    def _display(self, screen):
        # setup needs to happen AFTER the parent has been assigned
        if not self.setup:
            if not isinstance(self.parent, Selectable.ALLOWED_PARENTS):
                raise TypeError(
                    f"Component 'Selectable' cannot be added to a '{self.parent.__class__.__name__}' element"
                )
            self.setup = True

        # metrics data
        self.rect_metrics = self.parent.text.get_rect_metrics()
        self.rect_metrics_byline = self.parent.text.get_rect_metrics_byline()

        # if the text has changed, everything should be regenerated
        if self.parent.text.text != self.relevant_text:
            self.down_at = False
            self.up_at = False
            self.indices_state = False
            self.set_bounds_ = False
            self.relevant_text = self.parent.text.text

        for event in events.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.set_bounds_ = False
                self.indices_state = False
                if not self.down_at:
                    self.down_at = event.pos
                else:
                    self.down_at = False
                    self.up_at = False

            if event.type == pygame.MOUSEBUTTONUP:
                if self.down_at:
                    # can't have the same down_at and up_at
                    if event.pos == self.down_at:
                        self.down_at = False
                        self.up_at = False

                    else:
                        self.up_at = event.pos

            if self.indices_state:
                for textevent in key.get_all_events(True):
                    if textevent.key == pygame.K_c and textevent.mod & key.MOD:
                        key.remove_event(textevent)

                        start, end = self.get_bounds()
                        txt = self.parent.text.text[start : end + 1]
                        scrap.put(pygame.SCRAP_TEXT, txt)

        if self.set_bounds_:
            self.indices_state = self.set_bounds_

        elif self.down_at:
            pos = pygame.mouse.get_pos()
            rect = self.parent.location.resolve()

            if not self.indices_state or not self.up_at:

                p1 = pygame.mouse.get_pos() if not self.up_at else self.up_at
                p2 = self.down_at

                # if you've clicked but haven't dragged it shouldn't select the letter
                if p1 != p2:
                    self.indices_state = self._calculate_bounds(p1, p2)

        if self.indices_state:
            self._draw_bounds(screen, self.get_bounds())

    def get_bounds(self):
        if not self.indices_state:
            return False

        return [self.indices_state[0], self.indices_state[1]]

    def set_bounds(self, bounds):
        self.set_bounds_ = bounds

    def _calculate_bounds(self, p1, p2):

        # moving points to frame of text metrics
        xoff, yoff = self.parent.location.resolve().topleft
        p1 = [p1[0] - xoff, p1[1] - yoff]
        p2 = [p2[0] - xoff, p2[1] - yoff]

        text_rect = self.parent.text.get_rect()

        xmin, xmax = sorted([p1[0], p2[0]])
        ymin, ymax = sorted([p1[1], p2[1]])
        cursor_rect = pygame.Rect(xmin, ymin, xmax - xmin, ymax - ymin)

        # prevents weirdly selecting text across the screen from where you are
        if cursor_rect.colliderect(text_rect):
            line1 = line2 = 0

            for i in range(len(self.rect_metrics_byline)):
                rm = self.rect_metrics_byline[i][0]

                if rm.top <= p1[1] <= rm.bottom:
                    line1 = i

                if rm.top <= p2[1] <= rm.bottom:
                    line2 = i

            rm = self.rect_metrics_byline[-1][0]

            if rm.bottom < p1[1]:
                line1 = len(self.rect_metrics_byline) - 1
            if rm.bottom < p2[1]:
                line2 = len(self.rect_metrics_byline) - 1

            i1 = self._calculate_bounds_index(p1, line1, line2)
            i2 = self._calculate_bounds_index(p2, line2, line1)

            if i2 is not None and i1 is not None:
                return sorted([i1, i2])

        return False

    # handle the task of figuring out what index to use for the points
    def _calculate_bounds_index(self, point, linenum, otherlinenum):
        index = None

        line_rects = self.rect_metrics_byline[linenum]
        start_index = sum([len(l) for l in self.rect_metrics_byline[:linenum]])
        end_index = start_index + len(self.rect_metrics_byline[linenum])

        for i, rm in enumerate(line_rects, start_index):
            if rm.collidepoint(point):
                index = i

        if index is None:
            lb = line_rects[0].left
            rb = line_rects[-1].right

            if linenum < otherlinenum:
                if point[0] <= lb:
                    index = start_index - 1
                elif point[0] >= rb:
                    index = end_index
                else:
                    for i, rm in enumerate(line_rects, start_index):
                        if rm.left <= point[0] <= rm.right:
                            index = i

            elif linenum == otherlinenum:
                if point[0] <= lb:
                    index = start_index
                elif point[0] >= rb:
                    index = end_index
                else:
                    for i, rm in enumerate(line_rects, start_index):
                        if rm.left <= point[0] <= rm.right:
                            index = i

            else:
                if point[0] <= lb:
                    index = start_index - 1
                elif point[0] >= rb:
                    index = end_index
                else:
                    for i, rm in enumerate(line_rects, start_index):
                        if rm.left <= point[0] <= rm.right:
                            index = i

            # if it tries to select the line before the first line, it goes to index -1
            index = max(index, 0)

        return index

    def _draw_bounds(self, screen, bounds):
        imin, imax = bounds
        key_metrics = []

        count = 0
        for line in self.rect_metrics_byline:
            start = count
            stop = count + len(line) - 1

            # midline -> midline
            if start < imin and imax < stop:
                key_metrics += [imin, imax]

            # start of line -> end of line
            elif start >= imin and imax >= stop:
                key_metrics += [start, stop]

            # start of bound -> end of line
            elif start < imin and not stop < imin and imax >= stop:
                key_metrics += [imin, stop]

            # start of line -> end of bound
            elif start >= imin and imax < stop and not start > imax:
                key_metrics += [start, imax]

            if start > imax:
                break

            count += len(line)

        for i in range(0, len(key_metrics), 2):
            start = self.rect_metrics[key_metrics[i]]
            stop = self.rect_metrics[key_metrics[i + 1]]

            obsrect = pygame.Rect(
                (*start.topleft, stop.right - start.left, start.height)
            )
            obsrect.move_ip(self.parent.location.resolve().topleft)

            image.obscure(screen, self.select_color, area=obsrect)
