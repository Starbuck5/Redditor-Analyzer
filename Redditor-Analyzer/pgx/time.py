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
    time_scale = 1
    delta_time_cap = None
    _last_ticks = 0
    loops = 0

    @staticmethod
    def _tick(*args):
        time.clock.tick(*args)

        delta_ticks = pygame.time.get_ticks() - time._last_ticks
        time._last_ticks = pygame.time.get_ticks()
        time.delta_time = delta_ticks / 1000 * time.time_scale

        if time.delta_time_cap is not None:
            time.delta_time = min(time.delta_time, time.delta_time_cap)

        time.loops += 1

    @staticmethod
    def get_loops() -> int:
        """The number of times the program has gone through the game loop."""
        return time.loops
