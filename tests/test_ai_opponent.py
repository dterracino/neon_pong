"""Unit tests for AI opponent functionality."""
import os
import sys
import unittest
from unittest.mock import Mock

os.environ['SDL_AUDIODRIVER'] = 'dummy'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


class TestMenuOptions(unittest.TestCase):
    def test_menu_has_five_options(self):
        import pygame
        pygame.init()
        from src.scenes.menu_scene import MenuScene
        menu = MenuScene(Mock(), Mock(), Mock())
        self.assertEqual(len(menu.options), 5)

    def test_menu_option_labels(self):
        import pygame
        pygame.init()
        from src.scenes.menu_scene import MenuScene
        menu = MenuScene(Mock(), Mock(), Mock())
        self.assertEqual(menu.options[0], "1 Player (Easy)")
        self.assertEqual(menu.options[1], "1 Player (Normal)")
        self.assertEqual(menu.options[2], "1 Player (Hard)")
        self.assertEqual(menu.options[3], "2 Player")
        self.assertEqual(menu.options[4], "Quit")


class TestGameSceneAiParameter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        pygame.init()

    def _make_scene(self, **kwargs):
        from src.scenes.game_scene import GameScene
        return GameScene(Mock(), Mock(), Mock(), **kwargs)

    def test_ai_enabled_true(self):
        game = self._make_scene(ai_enabled=True)
        self.assertTrue(game.ai_enabled)
        self.assertIsNotNone(game.ai)

    def test_ai_enabled_with_difficulty(self):
        game_easy = self._make_scene(ai_enabled=True, ai_difficulty='easy')
        self.assertEqual(game_easy.ai_difficulty, 'easy')
        game_hard = self._make_scene(ai_enabled=True, ai_difficulty='hard')
        self.assertEqual(game_hard.ai_difficulty, 'hard')

    def test_ai_disabled(self):
        game = self._make_scene(ai_enabled=False)
        self.assertFalse(game.ai_enabled)
        self.assertIsNone(game.ai)

    def test_ai_disabled_by_default(self):
        game = self._make_scene()
        self.assertFalse(game.ai_enabled)
        self.assertIsNone(game.ai)


class TestAiClassIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        pygame.init()

    def test_ai_is_pong_ai_instance(self):
        from src.scenes.game_scene import GameScene
        from src.ai.pong_ai import PongAI
        game = GameScene(Mock(), Mock(), Mock(), ai_enabled=True, ai_difficulty='normal')
        self.assertIsInstance(game.ai, PongAI)

    def test_ai_has_required_methods(self):
        from src.scenes.game_scene import GameScene
        game = GameScene(Mock(), Mock(), Mock(), ai_enabled=True)
        self.assertTrue(hasattr(game.ai, 'update'))
        self.assertTrue(callable(game.ai.update))
        self.assertTrue(hasattr(game.ai, 'reset'))
        self.assertTrue(callable(game.ai.reset))


if __name__ == '__main__':
    unittest.main()
