"""Unit tests for background shader integration."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestBackgroundImports(unittest.TestCase):
    def test_renderer_imports(self):
        from src.rendering.renderer import Renderer
        self.assertIsNotNone(Renderer)

    def test_constants_import(self):
        from src.utils.constants import BACKGROUND_TYPE, WINDOW_WIDTH, WINDOW_HEIGHT
        self.assertIsNotNone(BACKGROUND_TYPE)
        self.assertIsNotNone(WINDOW_WIDTH)
        self.assertIsNotNone(WINDOW_HEIGHT)

    def test_shader_manager_imports(self):
        from src.managers.shader_manager import ShaderManager
        self.assertIsNotNone(ShaderManager)


class TestBackgroundRendererCode(unittest.TestCase):
    def _read_file(self, *parts):
        path = os.path.join(os.path.dirname(__file__), '..', *parts)
        with open(path) as f:
            return f.read()

    def test_game_has_update_time_call(self):
        content = self._read_file('src', 'game.py')
        self.assertIn('update_time', content)
        self.assertIn('self.renderer.update_time', content)

    def test_renderer_has_background_type(self):
        content = self._read_file('src', 'rendering', 'renderer.py')
        self.assertIn('BACKGROUND_TYPE', content)

    def test_renderer_has_background_program(self):
        content = self._read_file('src', 'rendering', 'renderer.py')
        self.assertIn('background_program', content)

    def test_renderer_has_update_time(self):
        content = self._read_file('src', 'rendering', 'renderer.py')
        self.assertIn('update_time', content)

    def test_renderer_tracks_time(self):
        content = self._read_file('src', 'rendering', 'renderer.py')
        self.assertIn('self.time', content)


if __name__ == '__main__':
    unittest.main()
