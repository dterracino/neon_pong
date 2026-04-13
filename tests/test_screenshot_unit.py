"""Unit tests for ScreenshotManager (no OpenGL required)."""
import os
import sys
import shutil
import tempfile
import unittest

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestScreenshotManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        pygame.init()
        cls.temp_dir = tempfile.mkdtemp(prefix='test_screenshots_')

    @classmethod
    def tearDownClass(cls):
        import pygame
        pygame.quit()
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)

    def _make_surface(self, w=800, h=600):
        import pygame
        surface = pygame.Surface((w, h))
        surface.fill((10, 5, 30))
        pygame.draw.circle(surface, (255, 113, 206), (w // 2, h // 2), 100)
        return surface

    def test_capture_creates_file(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        surface = self._make_surface()
        filepath = manager.capture(surface)
        self.assertTrue(os.path.exists(filepath))

    def test_captured_file_not_empty(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        filepath = manager.capture(self._make_surface())
        self.assertGreater(os.path.getsize(filepath), 0)

    def test_captured_filename_format(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        filepath = manager.capture(self._make_surface())
        filename = os.path.basename(filepath)
        self.assertTrue(filename.startswith('screenshot_'))
        self.assertTrue(filename.endswith('.png'))

    def test_capture_to_memory(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        surface = self._make_surface()
        result = manager.capture_to_memory(surface)
        self.assertIsNotNone(result)
        self.assertEqual(result.get_size(), surface.get_size())

    def test_get_last_screenshot(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        surface = self._make_surface()
        manager.capture_to_memory(surface)
        last = manager.get_last_screenshot()
        self.assertIsNotNone(last)
        self.assertEqual(last.get_size(), surface.get_size())

    def test_multiple_screenshots_have_different_names(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        surface = self._make_surface()
        path1 = manager.capture(surface)
        path2 = manager.capture(surface)
        self.assertNotEqual(path1, path2)

    def test_capture_without_saving_returns_empty_string(self):
        from src.utils.screenshot import ScreenshotManager
        manager = ScreenshotManager(self.temp_dir)
        before = len([f for f in os.listdir(self.temp_dir) if f.endswith('.png')])
        result = manager.capture(self._make_surface(), save_to_disk=False)
        after = len([f for f in os.listdir(self.temp_dir) if f.endswith('.png')])
        self.assertEqual(result, '')
        self.assertEqual(before, after)


if __name__ == '__main__':
    unittest.main()
