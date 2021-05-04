import platform

import pygame

from pgx import events
from pgx.time import time


# easy way to access keyboard input
class key:
    MOD = pygame.KMOD_META if platform.system() == "Darwin" else pygame.KMOD_CTRL

    downevents = []
    upevents = []

    pressed_memory = set()
    pressed = set()

    # called every tick by pgx.tick to get everything ready for next frame's query of input
    @staticmethod
    def _prepare():
        # getting input from the event queue
        downevents = []
        upevents = []

        for event in events.get():
            if event.type == pygame.KEYDOWN:
                event.key = key.__comp_replace(event.key)
                downevents.append(event)
                key.pressed_memory.add(event.key)

            if event.type == pygame.KEYUP:
                event.key = key.__comp_replace(event.key)
                upevents.append(event)
                key.pressed_memory.discard(event.key)

        # setting internal memory of the keys stuff this tick
        key.downevents = downevents
        key.upevents = upevents
        key.pressed = key.pressed_memory.copy()

    # ------------------------------------------------------------------------------------------#
    #                                      RESULTS INTERFACE                                    #
    # ------------------------------------------------------------------------------------------#

    @staticmethod
    def is_pressed(identifier: int, invisible: bool = False) -> bool:
        """Whether the specified key is currently pressed on the keyboard."""
        if identifier in key.pressed:
            if not invisible:
                key.pressed.remove(identifier)
            return True
        return False

    @staticmethod
    def is_just_pressed(identifier: int, invisible: bool = False) -> bool:
        """Whether the specified key was just pressed in the last tick."""
        for i, event in enumerate(key.downevents):
            if event.key == identifier:
                if not invisible:
                    del key.downevents[i]
                    key.pressed_memory.discard(identifier)
                    key.pressed.discard(identifier)
                return True
        return False

    @staticmethod
    def is_just_released(identifier: int, invisible: bool = False) -> bool:
        """Whether the specified key was just released in the last tick."""
        for i, event in enumerate(key.upevents):
            if event.key == identifier:
                if not invisible:
                    del key.upevents[i]
                return True
        return False

    @staticmethod
    def get_text_input(invisible: bool = False) -> str:
        """The text created by keydown events in the last tick."""
        out = ""
        for i, event in enumerate(key.downevents):
            if (
                event.unicode not in ["", "\b", "\t", "\r", "\n"]
                and event.mod & pygame.KMOD_CTRL
            ):
                out += event.unicode
                if not invisible:
                    del key.downevents[i]
                    key.pressed_memory.discard(event.key)
                    key.pressed.discard(event.key)
        return out

    @staticmethod
    def get_text_input_events(invisible=False) -> list:
        """The keydown events that relate to text in the last tick."""
        out = []
        for i, event in enumerate(key.downevents):
            if event.unicode:
                out.append(event)
                if not invisible:
                    del key.downevents[i]
                    key.pressed_memory.discard(event.key)
                    key.pressed.discard(event.key)
        return out

    @staticmethod
    def get_all_events(invisible=False) -> list:
        """Get all keydown events from last tick."""
        out = []
        for i, event in enumerate(key.downevents):
            out.append(event)
            if not invisible:
                del key.downevents[i]
                key.pressed_memory.discard(event.key)
                key.pressed.discard(event.key)
        return out

    @staticmethod
    def add_event(event) -> None:
        """Stole text events you need somewhere else? just re-add them to pgx.key"""
        if event.type == pygame.KEYDOWN:
            event.key = key.__comp_replace(event.key)
            key.downevents.append(event)
            key.pressed_memory.add(event.key)  # really?

        elif event.type == pygame.KEYUP:
            event.key = key.__comp_replace(event.key)
            key.upevents.append(event)
            key.pressed_memory.discard(event.key)  # really?

    @staticmethod
    def remove_event(event) -> None:
        """Invisibly processing text events and you find one you need to keep? Wipe them away."""
        if event.type == pygame.KEYDOWN:
            del key.downevents[key.downevents.index(event)]
            key.pressed_memory.discard(event.key)  # really?

        elif event.type == pygame.KEYUP:
            del key.upevents[key.upevents.index(event)]
            # key.pressed_memory.discard(event.key) # really?

    # ------------------------------------------------------------------------------------------#
    #                  COMPENSATING FOR NUMPAD KEYS HAVING DIFFERENT CONSTANTS                  #
    # ------------------------------------------------------------------------------------------#

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

    # called in _prepare to replace (or not) the keypad events with normal events
    @staticmethod
    def __comp_replace(eventkey):
        if key.compensate:
            if eventkey in key.corr_dict:
                eventkey = key.corr_dict[eventkey]
        return eventkey

    # should keypad 0 by returned as a normal 0? keypad delete?
    # defaults to True, or yes they should be normal
    # if you don't want it to do this simply set False
    @staticmethod
    def set_compensate(val: bool) -> None:
        """Set whether pgx.key treats keypad keys the same as the other keys."""
        key.compensate = val

    @staticmethod
    def get_compensate() -> bool:
        """Get whether pgx.key treats keypad keys the same as the other keys."""
        return key.compensate
