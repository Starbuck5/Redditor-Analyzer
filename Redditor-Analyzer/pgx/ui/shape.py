from abc import ABC, abstractmethod

import pygame


class shape:
    class Shape(ABC):
        @abstractmethod
        def __init__(self):
            pass

        @abstractmethod
        def display(self, screen):
            pass

        @abstractmethod
        def scale_to(self, scale):
            pass

        @abstractmethod
        def get_size(self):
            pass

        @abstractmethod
        def get_topleft(self):
            pass

        @abstractmethod
        def set_topleft(self, offset):
            pass

        # future addition perhaps
        def collides(self):
            pass

    class RectStyleShape(Shape):
        @abstractmethod
        def __init__(self):
            pass

        @abstractmethod
        def display(self, screen):
            pass

        def scale_to(self, scale):
            width = int(self.orig_width * scale)
            self.width = width if width or not self.orig_width else 1

            self.rect[2] = self.orig_rect[2] * scale
            self.rect[3] = self.orig_rect[3] * scale

        def get_size(self):
            return self.rect[2:4]

        def get_topleft(self):
            return self.rect[0:2]

        def set_topleft(self, offset):
            x, y = offset
            self.rect[0] = self.orig_rect[0] = x
            self.rect[1] = self.orig_rect[1] = y

    class Ellipse(RectStyleShape):
        def __init__(self, color, rect, width=0):
            self.color = color

            self.orig_rect = pygame.Rect(rect)
            self.rect = pygame.Rect(rect)

            self.orig_width = width
            self.width = width

        def display(self, screen):
            pygame.draw.ellipse(screen, self.color, self.rect, self.width)

    class Arc(RectStyleShape):
        def __init__(self, color, rect, start_angle, stop_angle, width=1):
            self.color = color

            self.orig_rect = pygame.Rect(rect)
            self.rect = pygame.Rect(rect)

            self.start_angle = start_angle
            self.stop_angle = stop_angle

            self.orig_width = width
            self.width = width

        def display(self, screen):
            pygame.draw.arc(
                screen,
                self.color,
                self.rect,
                self.start_angle,
                self.stop_angle,
                self.width,
            )

    class Rect(RectStyleShape):
        def __init__(self, color, rect, width=0):
            self.color = color

            self.orig_rect = pygame.Rect(rect)
            self.rect = pygame.Rect(rect)

            self.orig_width = width
            self.width = width

        def display(self, screen):
            pygame.draw.rect(screen, self.color, self.rect, self.width)

    class Circle(Shape):
        def __init__(self, color, center, radius, width=0):
            self.color = color

            self.orig_center = [*center]
            self.center = [*center]

            self.orig_radius = radius
            self.radius = radius

            self.orig_width = width
            self.width = width

        def display(self, screen):
            pygame.draw.circle(screen, self.color, self.center, self.radius, self.width)

        def scale_to(self, scale):
            radius = int(self.orig_radius * scale)
            self.radius = radius if radius or not self.orig_radius else 1

            width = int(self.orig_width * scale)
            self.width = width if width or not self.orig_width else 1

        def get_size(self):
            return [self.radius * 2, self.radius * 2]

        def get_topleft(self):
            return [
                self.center[0] - self.radius // 2,
                self.center[1] - self.radius // 2,
            ]

        def set_topleft(self, offset):
            self.center[0] = offset[0] + self.radius
            self.center[1] = offset[1] + self.radius

    def copy_points(points):
        return [[i, j] for i, j in points]

    def min_points(points):
        return [min([e[0] for e in points]), min([e[1] for e in points])]

    def max_points(points):
        return [max([e[0] for e in points]), max([e[1] for e in points])]

    def translate_points(points, x, y):
        for point in points:
            point[0] += x
            point[1] += y

    def norm_points(points):
        x, y = min_points(points)

        x = min(x, 0)
        y = min(y, 0)

        translate_points(points, -x, -y)
        return [-x, -y]

    def scale_points(points, scale):
        return [[i * scale, j * scale] for i, j in points]

    class PointStyleShape(Shape):
        def __init__(self, color, points):
            self.color = color

            self.orig_points = shape.copy_points(points)
            self.scaled_points = shape.copy_points(points)
            self.final_points = shape.copy_points(points)

            self.size = shape.max_points(self.scaled_points)
            self.topleft = [0, 0]

        @abstractmethod
        def display(self, screen):
            pass

        def scale_to(self, scale):
            self.scaled_points = shape.scale_points(self.orig_points, scale)
            self.final_points = shape.copy_points(self.scaled_points)
            shape.translate_points(self.final_points, *self.topleft)

            self.size = shape.max_points(self.scaled_points)

        def get_size(self):
            return self.size

        def get_topleft(self):
            return self.topleft

        def set_topleft(self, offset):
            self.topleft = offset

            self.final_points = shape.copy_points(self.scaled_points)
            shape.translate_points(self.final_points, *self.topleft)

    class Polygon(PointStyleShape):
        def __init__(self, color, points, width=0):
            self.orig_width = width
            self.width = width

            super().__init__(color, points)

        def scale_to(self, scale):
            width = int(self.orig_width * scale)
            self.width = width if width or not self.orig_width else 1

            super().scale_to(scale)

        def display(self, screen):
            pygame.draw.polygon(screen, self.color, self.final_points, self.width)

    class Line(PointStyleShape):
        def __init__(self, color, start_pos, end_pos, width=1):
            self.orig_width = width
            self.width = width

            super().__init__(color, [start_pos, end_pos])

        def scale_to(self, scale):
            width = int(self.orig_width * scale)
            self.width = width if width or not self.orig_width else 1

            super().scale_to(scale)

        def display(self, screen):
            pygame.draw.line(screen, self.color, *self.final_points, self.width)

    class Lines(PointStyleShape):
        def __init__(self, color, closed, points, width=1):
            self.orig_width = width
            self.width = width

            self.closed = closed

            super().__init__(color, points)

        def scale_to(self, scale):
            width = int(self.orig_width * scale)
            self.width = width if width or not self.orig_width else 1

            super().scale_to(scale)

        def display(self, screen):
            pygame.draw.lines(
                screen, self.color, self.closed, self.final_points, self.width
            )

    class AALine(PointStyleShape):
        def __init__(self, color, start_pos, end_pos, blend=1):
            self.blend = blend

            super().__init__(color, [start_pos, end_pos])

        def display(self, screen):
            pygame.draw.aaline(screen, self.color, *self.final_points, self.blend)

    class AALines(PointStyleShape):
        def __init__(self, color, closed, points, blend=1):
            self.closed = closed
            self.blend = blend

            super().__init__(color, points)

        def display(self, screen):
            pygame.draw.aalines(
                screen, self.color, self.closed, self.final_points, self.blend
            )
