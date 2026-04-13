"""Unit tests for post-processing style effect shaders."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

SHADER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shaders')
STYLE_SHADERS = ['scanlines', 'crt', 'vhs']


class TestStyleShaderFiles(unittest.TestCase):
    def _read_shader(self, name):
        path = os.path.join(SHADER_DIR, f'{name}.frag')
        self.assertTrue(os.path.exists(path), f'Shader not found: {name}.frag')
        with open(path) as f:
            return f.read()

    def test_all_style_shaders_exist(self):
        for name in STYLE_SHADERS:
            path = os.path.join(SHADER_DIR, f'{name}.frag')
            self.assertTrue(os.path.exists(path), f'Missing: {name}.frag')

    def test_shaders_have_version_declaration(self):
        for name in STYLE_SHADERS:
            content = self._read_shader(name)
            self.assertIn('#version 330', content)

    def test_shaders_have_main_function(self):
        for name in STYLE_SHADERS:
            content = self._read_shader(name)
            self.assertIn('void main()', content)

    def test_shaders_have_texture_uniform(self):
        for name in STYLE_SHADERS:
            content = self._read_shader(name)
            self.assertIn('uniform sampler2D tex', content)

    def test_shaders_have_time_uniform(self):
        for name in STYLE_SHADERS:
            content = self._read_shader(name)
            self.assertIn('uniform float time', content)

    def test_shaders_have_resolution_uniform(self):
        for name in STYLE_SHADERS:
            content = self._read_shader(name)
            self.assertIn('uniform vec2 resolution', content)


class TestStyleEffectConstants(unittest.TestCase):
    def test_post_effect_type_exists(self):
        from src.utils.constants import POST_EFFECT_TYPE
        self.assertIsNotNone(POST_EFFECT_TYPE)

    def test_post_effect_type_valid_value(self):
        from src.utils.constants import POST_EFFECT_TYPE
        self.assertIn(POST_EFFECT_TYPE, {'none', 'scanlines', 'crt', 'vhs'})


class TestPostProcessorIntegration(unittest.TestCase):
    def _read_post_process(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'rendering', 'post_process.py')
        with open(path) as f:
            return f.read()

    def test_has_apply_style_effect_method(self):
        content = self._read_post_process()
        self.assertIn('def apply_style_effect', content)

    def test_has_update_time_method(self):
        content = self._read_post_process()
        self.assertIn('def update_time', content)

    def test_imports_post_effect_type(self):
        content = self._read_post_process()
        self.assertIn('POST_EFFECT_TYPE', content)


if __name__ == '__main__':
    unittest.main()
