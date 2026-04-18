"""Unit tests for background shader files."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

SHADER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shaders')
BACKGROUND_SHADERS = [
    'background_starfield',
    'background_parallaxstarfield',
    'background_galaxytrip',
    'background_plasma',
    'background_waves',
    'background_retrowave',
    'background_retro',
]


class TestBackgroundShaderFiles(unittest.TestCase):
    def _read_shader(self, name):
        path = os.path.join(SHADER_DIR, f'{name}.frag')
        self.assertTrue(os.path.exists(path), f'Shader file not found: {name}.frag')
        with open(path) as f:
            return f.read()

    def test_all_shader_files_exist(self):
        for name in BACKGROUND_SHADERS:
            path = os.path.join(SHADER_DIR, f'{name}.frag')
            self.assertTrue(os.path.exists(path), f'Missing shader: {name}.frag')

    def test_shaders_have_version_declaration(self):
        for name in BACKGROUND_SHADERS:
            content = self._read_shader(name)
            self.assertIn('#version 330', content, f'{name}: missing #version 330')

    def test_shaders_have_main_function(self):
        for name in BACKGROUND_SHADERS:
            content = self._read_shader(name)
            self.assertIn('void main()', content, f'{name}: missing void main()')

    def test_shaders_have_time_uniform(self):
        for name in BACKGROUND_SHADERS:
            content = self._read_shader(name)
            self.assertIn('uniform float time', content,
                          f'{name}: missing uniform float time')

    def test_shaders_have_resolution_uniform(self):
        for name in BACKGROUND_SHADERS:
            content = self._read_shader(name)
            self.assertIn('uniform vec2 resolution', content,
                          f'{name}: missing uniform vec2 resolution')


class TestBackgroundConstants(unittest.TestCase):
    def test_background_type_constant_exists(self):
        from src.utils.constants import BACKGROUND_TYPE
        self.assertIsNotNone(BACKGROUND_TYPE)

    def test_background_type_has_valid_value(self):
        from src.utils.constants import BACKGROUND_TYPE
        valid_values = ('starfield', 'parallaxstarfield', 'galaxytrip', 'plasma', 'waves', 'retrowave', 'retro', 'solid')
        self.assertIn(BACKGROUND_TYPE, valid_values)


if __name__ == '__main__':
    unittest.main()
