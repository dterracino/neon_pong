"""Unit tests for pygame text rendering API."""
import os
import sys
import unittest

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestFontLoading(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        import pygame
        pygame.quit()

    def test_default_font_loads(self):
        import pygame
        font = pygame.font.Font(None, 32)
        self.assertIsNotNone(font)

    def test_multiple_sizes_load(self):
        import pygame
        for size in [24, 32, 48, 64, 72]:
            font = pygame.font.Font(None, size)
            self.assertIsNotNone(font)

    def test_text_renders_to_surface(self):
        import pygame
        font = pygame.font.Font(None, 48)
        surface = font.render("Test Text", True, (255, 255, 255))
        self.assertIsNotNone(surface)
        self.assertGreater(surface.get_width(), 0)
        self.assertGreater(surface.get_height(), 0)

    def test_surface_converts_to_texture_data(self):
        import pygame
        font = pygame.font.Font(None, 48)
        surface = font.render("Test Text", True, (255, 255, 255))
        data = pygame.image.tostring(surface, 'RGBA', True)
        self.assertGreater(len(data), 0)


if __name__ == '__main__':
    unittest.main()
