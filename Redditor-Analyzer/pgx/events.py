import pygame

"""
cool if there was a remove_next(type), which waits until it sees something and removes it
maybe a remove(event)
and a post(event)

do we need to emulate more of pygame.event?
"""

# allows multiple locations to peek at what the event queue had to say since last tick
# the event queue kicks up keydown events, keyup events, and exit events, along with other things
class events:
    CLICK_ADD_DELAY = 500  # msec

    _tickevents = []  # used to store event queue offloads

    _last_click_msec = 0
    _clickcount = 1

    # called every tick by pgx.tick()
    @staticmethod
    def _update():
        events._tickevents.clear()
        for event in pygame.event.get():
            events._tickevents.append(event)

            # left click events are given a clickcount variable to see whether
            # it is a double or triple or arbitrary number click
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    ct = pygame.time.get_ticks()
                    lt = events._last_click_msec
                    if ct - lt < events.CLICK_ADD_DELAY:
                        events._clickcount += 1
                    else:
                        events._clickcount = 1

                    events._last_click_msec = ct
                    event.clickcount = events._clickcount
                else:
                    event.clickcount = 1

    # public method to access the updated list of events
    @staticmethod
    def get() -> list:
        """Returns the previous tick’s events."""
        return events._tickevents.copy()
