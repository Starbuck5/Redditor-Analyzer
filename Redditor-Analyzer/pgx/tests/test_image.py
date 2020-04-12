import unittest
import pygame

from .. import pgx

pgx.init([600, 400])


class ImageTest(unittest.TestCase):
    screen = pygame.display.set_mode([600, 400])

    # def setUp(self):

    def test_load(self):
        image = pgx.image.load("pgx\\tests\\test_assets\\image.tif")
        self.assertIsInstance(image, pygame.Surface)
        self.assertEqual(128, image.get_width())
        self.assertEqual(128, image.get_height())

    # def tearDown(self)


def run():
    unittest.main(module=__name__)
