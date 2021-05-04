import pygame

PG2 = pygame.version.vernum[0] == 2


class null_backend:
    @staticmethod
    def init():
        pass

    @staticmethod
    def get_init():
        return True

    @staticmethod
    def get(type_cons):
        return ""

    @staticmethod
    def get_types():
        return []

    @staticmethod
    def put(type_cons, data):
        return None

    @staticmethod
    def contains(type_cons):
        return False

    @staticmethod
    def lost():
        return True

    @staticmethod
    def set_mode(mode):
        pass


class scrap_backend:
    @staticmethod
    def init():
        pygame.scrap.init()

    @staticmethod
    def get_init():
        return pygame.scrap.get_init()

    @staticmethod
    def get(type_cons):
        if type_cons == pygame.SCRAP_TEXT:
            if PG2:
                out = pygame.scrap.get("text/plain;charset=utf-8")
            else:
                out = pygame.scrap.get(type_cons)

            try:
                out = out.decode("utf-8")
            except UnicodeDecodeError:
                return ""

            if not PG2:
                out = out[:-1]

            return out

        return pygame.scrap.get(type_cons)

    @staticmethod
    def get_types():
        return pygame.scrap.get_types()

    @staticmethod
    def put(type_cons, data):
        if type_cons == pygame.SCRAP_TEXT:
            data = bytes(data, "utf-8")
            if PG2:
                pygame.scrap.put("text/plain;charset=utf-8", data)
            else:
                pygame.scrap.put(pygame.SCRAP_TEXT, data)

            return

        pygame.scrap.put(type_cons, data)

    @staticmethod
    def contains(type_cons):
        return pygame.scrap.contains(type_cons)

    @staticmethod
    def lost():
        return pygame.scrap.lost()

    @staticmethod
    def set_mode(mode):
        pygame.scrap.set_mode(mode)


from pygame import scrap as pgscrap

backend = null_backend
if pgscrap:  # MissingModule = False, so this tests if it isn't MissingModule
    backend = scrap_backend


class scrap:
    @staticmethod
    def init():
        backend.init()

    @staticmethod
    def get_init():
        return backend.get_init()

    @staticmethod
    def get(type_cons):
        return backend.get(type_cons)

    @staticmethod
    def get_types():
        return backend.get_types()

    @staticmethod
    def put(type_cons, data):
        backend.put(type_cons, data)

    @staticmethod
    def contains(type_cons):
        return backend.contains(type_cons)

    @staticmethod
    def lost():
        return backend.scrap.lost()

    @staticmethod
    def set_mode(mode):
        backend.set_mode(mode)
