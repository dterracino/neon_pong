"""Unit tests for FPS display rendering logic."""
import os
import sys
import unittest

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestFpsRenderingLogic(unittest.TestCase):
    def setUp(self):
        from src.utils.fps_counter import FPSCounter
        self.counter = FPSCounter(average_window=1.0)
        self.counter.visible = True
        for _ in range(100):
            self.counter.update(0.016)

    def test_instant_fps_near_60(self):
        instant, _, _, _, _ = self.counter.get_metrics()
        self.assertGreater(instant, 55)
        self.assertLess(instant, 65)

    def test_average_fps_near_60(self):
        _, average, _, _, _ = self.counter.get_metrics()
        self.assertGreater(average, 55)
        self.assertLess(average, 65)


class TestRendererDirectDraw(unittest.TestCase):
    def test_renderer_has_draw_text_direct(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'rendering', 'renderer.py')
        with open(path) as f:
            content = f.read()
        self.assertIn('def draw_text_direct', content)


class TestFpsDisplayConfiguration(unittest.TestCase):
    def test_configuration_constants_importable(self):
        from src.utils.constants import (
            FPS_DISPLAY_SHOW_INSTANT,
            FPS_DISPLAY_SHOW_AVERAGE,
            FPS_DISPLAY_SHOW_1_PERCENT,
            FPS_DISPLAY_SHOW_0_1_PERCENT,
        )
        self.assertIsNotNone(FPS_DISPLAY_SHOW_INSTANT)
        self.assertIsNotNone(FPS_DISPLAY_SHOW_AVERAGE)
        self.assertIsNotNone(FPS_DISPLAY_SHOW_1_PERCENT)
        self.assertIsNotNone(FPS_DISPLAY_SHOW_0_1_PERCENT)


if __name__ == '__main__':
    unittest.main()
