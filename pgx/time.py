import pygame.time

"""
Features to perhaps add:

These are simple to implement but are frequently used.
Code abstraction could be helpful here.

Timers - counts down a time
Loopers - goes through a variety of states with a delay Ex: [0, 1, 2, 3, 0, 1, 2, 3, ...] every n seconds
Stopwatches - keep track of time after it starts
"""


class time:
    clock = pygame.time.Clock()
    delta_time = 0.0
    _last_ticks = 0

    @staticmethod
    def _tick(*args):
        time.clock.tick(*args)

        delta_ticks = pygame.time.get_ticks() - time._last_ticks
        time._last_ticks = pygame.time.get_ticks()
        time.delta_time = delta_ticks / 1000
