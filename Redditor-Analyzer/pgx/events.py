import pygame

# allows multiple locations to peek at what the event queue had to say since last tick
# the event queue kicks up keydown events, keyup events, and exit events, along with other things
class events:
    tickevents = []  # used to store event queue offloads

    # called every tick by pgx.tick()
    @staticmethod
    def _update():
        events.tickevents = []
        for event in pygame.event.get():
            events.tickevents.append(event)

    # public method to access the updated list of events
    @staticmethod
    def get():
        return events.tickevents.copy()
