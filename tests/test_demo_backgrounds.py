"""Unit tests for demo_backgrounds module structure."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

SHADER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'shaders')


class TestDemoBackgroundsStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import demo_backgrounds
        cls.module = demo_backgrounds

    def test_shaders_dict_exists(self):
        self.assertTrue(hasattr(self.module, 'SHADERS'))

    def test_shaders_dict_has_five_entries(self):
        self.assertEqual(len(self.module.SHADERS), 5)

    def test_expected_shader_ids_present(self):
        expected = {'starfield', 'plasma', 'waves', 'retrowave', 'retro'}
        self.assertEqual(set(self.module.SHADERS.keys()), expected)

    def test_demo_class_exists(self):
        self.assertTrue(hasattr(self.module, 'BackgroundShaderDemo'))

    def test_each_shader_has_required_fields(self):
        required_fields = {'name', 'vertex', 'fragment', 'key', 'description'}
        for shader_id, config in self.module.SHADERS.items():
            for field in required_fields:
                self.assertIn(field, config, f'{shader_id} missing field: {field}')

    def test_shader_files_exist_on_disk(self):
        for shader_id, config in self.module.SHADERS.items():
            for kind in ('vertex', 'fragment'):
                path = os.path.join(SHADER_DIR, config[kind])
                self.assertTrue(os.path.exists(path),
                                f'{shader_id} {kind} file not found: {config[kind]}')


if __name__ == '__main__':
    unittest.main()
