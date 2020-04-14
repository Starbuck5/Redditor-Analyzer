import pygame
from pgx import events
from pgx.time import time

"""
feature request: pgx.key.sim_press, sim_release, simulating press or release
-user can already use event queue post to do this

make a kwarg for all the checker ones that remove the event from the event queue if found
"""

"""
I now want to completely change up the interface to make it more amenable to not repeating keys

id being a key constant or a string
invisible being whether it deletes the event when it finds a match

class key:

    def _prepare()

    def is_pressed(id, invisible = False)

    def is_just_pressed(id, invisible = False)

    def is_just_released(id, invisible = False)


"""

# easy way to access keyboard input
# all keys returned in number format, checkable like "pygame.K_0 in pgx.key.downs()"
class key:
    Kdowns = []
    Kdownevents = []
    Kups = []
    Kpressed = []

    compensate = True
    corr_dict = {
        pygame.K_KP0: pygame.K_0,
        pygame.K_KP1: pygame.K_1,
        pygame.K_KP2: pygame.K_2,
        pygame.K_KP3: pygame.K_3,
        pygame.K_KP4: pygame.K_4,
        pygame.K_KP5: pygame.K_5,
        pygame.K_KP6: pygame.K_6,
        pygame.K_KP7: pygame.K_7,
        pygame.K_KP8: pygame.K_8,
        pygame.K_KP9: pygame.K_9,
        pygame.K_KP_PERIOD: pygame.K_PERIOD,
        pygame.K_KP_DIVIDE: pygame.K_SLASH,
        pygame.K_KP_MULTIPLY: pygame.K_ASTERISK,
        pygame.K_KP_MINUS: pygame.K_MINUS,
        pygame.K_KP_PLUS: pygame.K_PLUS,
        pygame.K_KP_ENTER: pygame.K_RETURN,
        pygame.K_KP_EQUALS: pygame.K_EQUALS,
    }

    _timesince = {}  # time since keydown events
    # formatted as id: [is_initial (0 or 1), milliseconds held]
    _repsettings = {}  # repeat setting
    # formatted as id: [initial ms, delay ms]
    # ex: {pygame.K_a: (500, 10), pygame.K_BACKSPACE: (500, 10)}

    # called in _prepare to replace (or not) the keypad events with normal events
    @staticmethod
    def __comp_replace(eventkey):
        if key.compensate:
            if eventkey in key.corr_dict:
                eventkey = key.corr_dict[eventkey]
        return eventkey

    # called every tick by pgx.tick to get everything ready for next frame's query of input
    @staticmethod
    def _prepare():
        # getting input from the event queue
        downs = []
        downevents = []
        ups = []
        upevents = []
        for event in events.get():
            if event.type == pygame.KEYDOWN:
                event.key = key.__comp_replace(event.key)
                downs.append(event.key)
                downevents.append(event)

            if event.type == pygame.KEYUP:
                event.key = key.__comp_replace(event.key)
                ups.append(event.key)
                upevents.append(event)

        # figuring out what keys are pressed
        overall = pygame.key.get_pressed()
        pressed = []
        for i in range(len(overall)):
            if overall[i]:  # int of 1 = True, int of 0 = False
                pressed.append(key.__comp_replace(i))

        # handling key specific repeats
        for trackedkey in key._timesince:
            if trackedkey in pressed:
                key._timesince[trackedkey][1] += time.delta_time * 1000
            else:
                key._timesince[trackedkey][1] = 0

        for press in pressed:
            if press not in key._timesince:
                key._timesince[press] = [0, 0]

        for trackedkey in key._timesince:
            if trackedkey in key._repsettings:
                if (
                    key._timesince[trackedkey][1]
                    > key._repsettings[trackedkey][key._timesince[trackedkey][0]]
                ):
                    key._timesince[trackedkey][1] = 0
                    key._timesince[trackedkey][0] = 1
                    downs.append(trackedkey)
                    downevents.append(pygame.event.Event(2))
                    downevents[-1].key = trackedkey
                    downevents[-1].unicode = pygame.key.name(trackedkey)
                    """
                    This key event emulation seems to work but it's not an exact replica
                    """

        # setting internal memory of the keys stuff this tick
        key.Kdowns = downs
        key.Kdownevents = downevents
        key.Kups = ups
        key.Kupevents = upevents
        key.Kpressed = pressed

    # should keypad 0 by returned as a normal 0? keypad delete?
    # defaults to True, or yes they should be normal
    # if you don't want it to do this simply set False
    @staticmethod
    def set_compensate(boolean):
        key.compensate = boolean

    # keys that were pressed down during the last tick
    @staticmethod
    def downs():
        return key.Kdowns

    # actual keydown events from last tick
    @staticmethod
    def downevents():
        return key.Kdownevents

    # keys that were released during the last tick
    @staticmethod
    def ups():
        return key.Kups

    # actual keyup events from last tick
    @staticmethod
    def upevents():
        return key.Kupevents

    # keys that are currently pressed
    @staticmethod
    def pressed():
        return key.Kpressed

    # key specific repeats
    @staticmethod
    def set_repeat(keyid, delay=0, interval=0):
        if delay < 0:
            raise ValueError("Delay has to be a positive integer")
        if interval < 0:
            raise ValueError("Interval has to be a positive integer")

        if delay == 0:
            if keyid not in key._repsettings:
                pass
            else:
                del key._repsettings[keyid]
            return

        if interval == 0:
            interval = delay

        key._repsettings[keyid] = (delay, interval)

    # getting key specific repeats
    @staticmethod
    def get_repeat(keyid):
        if keyid not in key._repsettings:
            raise ValueError("This key is not repeated")
        return key._repsettings[keyid]

    # getting all current repeat settings
    @staticmethod
    def get_all_repeats():
        return key._repsettings
