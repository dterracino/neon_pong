"""
Test AI opponent functionality
"""
import sys
import os
from unittest.mock import Mock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_menu_options():
    """Test that menu has correct options"""
    from src.scenes.menu_scene import MenuScene
    
    # Mock dependencies using unittest.mock
    scene_manager = Mock()
    renderer = Mock()
    audio_manager = Mock()
    
    menu = MenuScene(scene_manager, renderer, audio_manager)
    
    # Check menu options
    assert len(menu.options) == 5, f"Expected 5 menu options, got {len(menu.options)}"
    assert menu.options[0] == "1 Player (Easy)", f"Expected first option to be '1 Player (Easy)', got '{menu.options[0]}'"
    assert menu.options[1] == "1 Player (Normal)", f"Expected second option to be '1 Player (Normal)', got '{menu.options[1]}'"
    assert menu.options[2] == "1 Player (Hard)", f"Expected third option to be '1 Player (Hard)', got '{menu.options[2]}'"
    assert menu.options[3] == "2 Player", f"Expected fourth option to be '2 Player', got '{menu.options[3]}'"
    assert menu.options[4] == "Quit", f"Expected fifth option to be 'Quit', got '{menu.options[4]}'"
    
    print("✓ Menu options test passed")
    return True


def test_game_scene_ai_parameter():
    """Test that GameScene accepts ai_enabled and ai_difficulty parameters"""
    import pygame
    pygame.init()
    
    try:
        from src.scenes.game_scene import GameScene
        
        # Mock dependencies using unittest.mock
        scene_manager = Mock()
        renderer = Mock()
        audio_manager = Mock()
        
        # Test with AI enabled (default difficulty)
        game_ai = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True)  # type: ignore
        assert game_ai.ai_enabled == True, "Expected ai_enabled to be True"
        assert game_ai.ai is not None, "Expected AI to be initialized"
        
        # Test with AI enabled and specific difficulty
        game_ai_easy = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True, ai_difficulty='easy')  # type: ignore
        assert game_ai_easy.ai_enabled == True, "Expected ai_enabled to be True"
        assert game_ai_easy.ai_difficulty == 'easy', "Expected ai_difficulty to be 'easy'"
        
        game_ai_hard = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True, ai_difficulty='hard')  # type: ignore
        assert game_ai_hard.ai_enabled == True, "Expected ai_enabled to be True"
        assert game_ai_hard.ai_difficulty == 'hard', "Expected ai_difficulty to be 'hard'"
        
        # Test with AI disabled
        game_2p = GameScene(scene_manager, renderer, audio_manager, ai_enabled=False)  # type: ignore
        assert game_2p.ai_enabled == False, "Expected ai_enabled to be False"
        assert game_2p.ai is None, "Expected AI to not be initialized"
        
        # Test default (should be False)
        game_default = GameScene(scene_manager, renderer, audio_manager)  # type: ignore
        assert game_default.ai_enabled == False, "Expected default ai_enabled to be False"
        assert game_default.ai is None, "Expected AI to not be initialized"
        
        print("✓ GameScene AI parameter test passed")
        return True
    except Exception as e:
        print(f"✗ GameScene AI parameter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_class_integration():
    """Test that PongAI class is properly integrated"""
    import pygame
    pygame.init()
    
    try:
        from src.scenes.game_scene import GameScene
        from src.ai.pong_ai import PongAI
        
        # Mock dependencies using unittest.mock
        scene_manager = Mock()
        renderer = Mock()
        audio_manager = Mock()
        
        game = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True, ai_difficulty='normal')  # type: ignore
        
        # Check that AI object exists and is correct type
        assert hasattr(game, 'ai'), "Expected GameScene to have 'ai' attribute"
        assert game.ai is not None, "Expected AI to be initialized"
        assert isinstance(game.ai, PongAI), f"Expected AI to be PongAI instance, got {type(game.ai)}"
        
        # Check that AI has required methods
        assert hasattr(game.ai, 'update'), "Expected AI to have 'update' method"
        assert callable(game.ai.update), "Expected AI.update to be callable"
        assert hasattr(game.ai, 'reset'), "Expected AI to have 'reset' method"
        assert callable(game.ai.reset), "Expected AI.reset to be callable"
        
        print("✓ AI class integration test passed")
        return True
    except Exception as e:
        print(f"✗ AI class integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("Testing AI Opponent Implementation\n")
    
    results = []
    results.append(test_menu_options())
    results.append(test_game_scene_ai_parameter())
    results.append(test_ai_class_integration())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All AI opponent tests PASSED!")
        sys.exit(0)
    else:
        print("✗ Some AI opponent tests FAILED!")
        sys.exit(1)
