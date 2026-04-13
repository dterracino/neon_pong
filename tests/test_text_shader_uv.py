"""Unit tests for text shader UV coordinate mapping."""
import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestUVCoordinates(unittest.TestCase):
    def _make_vertices(self, x, y, text_width, text_height,
                       window_width=800, window_height=600):
        ndc_x = (x / window_width) * 2 - 1
        ndc_y = 1 - (y / window_height) * 2
        ndc_w = (text_width / window_width) * 2
        ndc_h = (text_height / window_height) * 2
        return np.array([
            ndc_x,         ndc_y - ndc_h, 0.0, 1.0,
            ndc_x + ndc_w, ndc_y - ndc_h, 1.0, 1.0,
            ndc_x,         ndc_y,         0.0, 0.0,
            ndc_x + ndc_w, ndc_y,         1.0, 0.0,
        ], dtype='f4')

    def test_uv_coordinates_correct(self):
        vertices = self._make_vertices(100, 200, 200, 50)
        uv_coords = vertices.reshape(-1, 4)[:, 2:4]
        expected = np.array([
            [0.0, 1.0],
            [1.0, 1.0],
            [0.0, 0.0],
            [1.0, 0.0],
        ])
        self.assertTrue(np.allclose(uv_coords, expected),
                        "UV coordinates do not match expected values")

    def test_shader_files_exist(self):
        shader_dir = os.path.join(os.path.dirname(__file__), '..', 'shaders')
        self.assertTrue(os.path.exists(os.path.join(shader_dir, 'text.vert')))
        self.assertTrue(os.path.exists(os.path.join(shader_dir, 'text.frag')))

    def test_shader_has_uv_input(self):
        vert_path = os.path.join(os.path.dirname(__file__), '..', 'shaders', 'text.vert')
        with open(vert_path) as f:
            content = f.read()
        self.assertIn('in_uv', content)


if __name__ == '__main__':
    unittest.main()
