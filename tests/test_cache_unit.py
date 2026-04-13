"""Unit tests for text rendering cache data structures."""
import os
import sys
import unittest

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestCacheKeyGeneration(unittest.TestCase):
    def test_identical_keys_are_equal(self):
        key1 = ("Hello", 32, (255, 255, 255), None)
        key2 = ("Hello", 32, (255, 255, 255), None)
        self.assertEqual(key1, key2)

    def test_different_size_not_equal(self):
        key1 = ("Hello", 32, (255, 255, 255), None)
        key3 = ("Hello", 48, (255, 255, 255), None)
        self.assertNotEqual(key1, key3)

    def test_different_color_not_equal(self):
        key1 = ("Hello", 32, (255, 255, 255), None)
        key4 = ("Hello", 32, (255, 0, 0), None)
        self.assertNotEqual(key1, key4)

    def test_different_text_not_equal(self):
        key1 = ("Hello", 32, (255, 255, 255), None)
        key5 = ("World", 32, (255, 255, 255), None)
        self.assertNotEqual(key1, key5)

    def test_keys_are_hashable(self):
        key1 = ("Hello", 32, (255, 255, 255), None)
        key2 = ("Hello", 32, (255, 255, 255), None)
        cache = {key1: "value1"}
        self.assertEqual(cache[key2], "value1")


class TestCacheAccessTracking(unittest.TestCase):
    def test_access_count(self):
        access_count = {}
        keys = [
            ("Item1", 32, (255, 255, 255), None),
            ("Item2", 32, (255, 255, 255), None),
            ("Item1", 32, (255, 255, 255), None),
            ("Item3", 32, (255, 255, 255), None),
            ("Item1", 32, (255, 255, 255), None),
        ]
        for key in keys:
            access_count[key] = access_count.get(key, 0) + 1
        self.assertEqual(access_count[keys[0]], 3)
        self.assertEqual(access_count[keys[1]], 1)
        self.assertEqual(access_count[keys[3]], 1)

    def test_lru_sort_order(self):
        access_count = {
            ("A", 32, (255, 255, 255), None): 3,
            ("B", 32, (255, 255, 255), None): 1,
            ("C", 32, (255, 255, 255), None): 1,
        }
        sorted_items = sorted(access_count.items(), key=lambda x: x[1])
        self.assertEqual(sorted_items[0][1], 1)
        self.assertEqual(sorted_items[-1][1], 3)


class TestCacheCleanupLogic(unittest.TestCase):
    def _build_cache(self, size=15):
        cache = {}
        access_count = {}
        for i in range(size):
            key = (f"Item{i}", 32, (255, 255, 255), None)
            cache[key] = f"Surface{i}"
            access_count[key] = size - i
        return cache, access_count

    def test_cleanup_reduces_to_max_size(self):
        cache, access_count = self._build_cache(15)
        max_cache_size = 10
        if len(cache) > max_cache_size:
            sorted_items = sorted(access_count.items(), key=lambda x: x[1])
            items_to_remove = len(cache) - max_cache_size + 2
            for key, _ in sorted_items[:items_to_remove]:
                del cache[key]
                del access_count[key]
        self.assertEqual(len(cache), 8)

    def test_least_used_removed_most_used_kept(self):
        cache, access_count = self._build_cache(15)
        sorted_items = sorted(access_count.items(), key=lambda x: x[1])
        items_to_remove = len(cache) - 10 + 2
        for key, _ in sorted_items[:items_to_remove]:
            del cache[key]
            del access_count[key]
        self.assertNotIn(("Item14", 32, (255, 255, 255), None), cache)
        self.assertIn(("Item0", 32, (255, 255, 255), None), cache)


class TestRendererCacheAttributes(unittest.TestCase):
    def test_renderer_has_cache_methods(self):
        import pygame
        pygame.init()
        from src.rendering.renderer import Renderer
        self.assertTrue(hasattr(Renderer, '_manage_text_cache'))
        self.assertTrue(hasattr(Renderer, 'get_text_cache_stats'))


if __name__ == '__main__':
    unittest.main()
