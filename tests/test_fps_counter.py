"""Unit tests for FPS counter functionality."""
import os
import sys
import unittest

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestFpsCounterImports(unittest.TestCase):
    def test_fps_counter_importable(self):
        from src.utils.fps_counter import FPSCounter
        self.assertIsNotNone(FPSCounter)

    def test_fps_constants_importable(self):
        from src.utils.constants import (
            FPS_DISPLAY_SHOW_INSTANT,
            FPS_DISPLAY_SHOW_AVERAGE,
            FPS_DISPLAY_SHOW_1_PERCENT,
            FPS_DISPLAY_SHOW_0_1_PERCENT,
            FPS_DISPLAY_AVERAGE_WINDOW,
            FPS_DISPLAY_POSITION_X,
            FPS_DISPLAY_POSITION_Y,
        )


class TestFpsCounterBasic(unittest.TestCase):
    def setUp(self):
        from src.utils.fps_counter import FPSCounter
        self.counter = FPSCounter(average_window=1.0)

    def test_starts_invisible(self):
        self.assertFalse(self.counter.is_visible())

    def test_toggle_makes_visible(self):
        self.counter.toggle_visibility()
        self.assertTrue(self.counter.is_visible())

    def test_double_toggle_hides(self):
        self.counter.toggle_visibility()
        self.counter.toggle_visibility()
        self.assertFalse(self.counter.is_visible())

    def test_update_produces_metrics(self):
        self.counter.update(0.016)
        instant, average, low_1, low_01, frame_ms = self.counter.get_metrics()
        self.assertGreater(instant, 55)
        self.assertLess(instant, 65)


class TestFpsCounterPercentiles(unittest.TestCase):
    def setUp(self):
        from src.utils.fps_counter import FPSCounter
        self.counter = FPSCounter(average_window=10.0)
        for i in range(100):
            dt = 0.033 if i % 20 == 0 else 0.016
            self.counter.update(dt)

    def test_average_is_reasonable(self):
        _, average, _, _, _ = self.counter.get_metrics()
        self.assertGreater(average, 45)
        self.assertLess(average, 65)

    def test_low_percentile_below_average(self):
        _, average, low_1, _, _ = self.counter.get_metrics()
        self.assertLess(low_1, average)


class TestFpsCounterGameIntegration(unittest.TestCase):
    def _read_game(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'src', 'game.py')
        with open(path) as f:
            return f.read()

    def test_game_imports_fps_counter(self):
        content = self._read_game()
        self.assertIn('FPSCounter', content)

    def test_game_initialises_fps_counter(self):
        content = self._read_game()
        self.assertIn('self.fps_counter = FPSCounter', content)

    def test_game_calls_fps_update(self):
        content = self._read_game()
        self.assertIn('self.fps_counter.update', content)

    def test_game_checks_fps_visibility(self):
        content = self._read_game()
        self.assertIn('self.fps_counter.is_visible', content)

    def test_game_has_f3_toggle(self):
        content = self._read_game()
        self.assertIn('K_F3', content)

    def test_game_has_fps_render_method(self):
        content = self._read_game()
        self.assertIn('_render_fps_display', content)


if __name__ == '__main__':
    unittest.main()
