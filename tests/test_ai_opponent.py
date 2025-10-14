"""
Test AI opponent functionality
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_menu_options():
    """Test that menu has correct options"""
    from src.scenes.menu_scene import MenuScene
    
    # Mock dependencies
    class MockSceneManager:
        pass
    
    class MockRenderer:
        pass
    
    class MockAudioManager:
        pass
    
    scene_manager = MockSceneManager()
    renderer = MockRenderer()
    audio_manager = MockAudioManager()
    
    menu = MenuScene(scene_manager, renderer, audio_manager)
    
    # Check menu options
    assert len(menu.options) == 3, f"Expected 3 menu options, got {len(menu.options)}"
    assert menu.options[0] == "1 Player", f"Expected first option to be '1 Player', got '{menu.options[0]}'"
    assert menu.options[1] == "2 Player", f"Expected second option to be '2 Player', got '{menu.options[1]}'"
    assert menu.options[2] == "Quit", f"Expected third option to be 'Quit', got '{menu.options[2]}'"
    
    print("✓ Menu options test passed")
    return True


def test_game_scene_ai_parameter():
    """Test that GameScene accepts ai_enabled parameter"""
    import pygame
    pygame.init()
    
    try:
        from src.scenes.game_scene import GameScene
        
        # Mock dependencies
        class MockSceneManager:
            pass
        
        class MockRenderer:
            def begin_frame(self):
                pass
            def end_frame(self):
                pass
        
        class MockAudioManager:
            def play_sound(self, sound, pitch_variation=False):
                pass
        
        scene_manager = MockSceneManager()
        renderer = MockRenderer()
        audio_manager = MockAudioManager()
        
        # Test with AI enabled
        game_ai = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True)
        assert game_ai.ai_enabled == True, "Expected ai_enabled to be True"
        
        # Test with AI disabled
        game_2p = GameScene(scene_manager, renderer, audio_manager, ai_enabled=False)
        assert game_2p.ai_enabled == False, "Expected ai_enabled to be False"
        
        # Test default (should be False)
        game_default = GameScene(scene_manager, renderer, audio_manager)
        assert game_default.ai_enabled == False, "Expected default ai_enabled to be False"
        
        print("✓ GameScene AI parameter test passed")
        return True
    except Exception as e:
        print(f"✗ GameScene AI parameter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_paddle_method_exists():
    """Test that AI paddle update method exists"""
    import pygame
    pygame.init()
    
    try:
        from src.scenes.game_scene import GameScene
        
        # Mock dependencies
        class MockSceneManager:
            pass
        
        class MockRenderer:
            def begin_frame(self):
                pass
            def end_frame(self):
                pass
        
        class MockAudioManager:
            def play_sound(self, sound, pitch_variation=False):
                pass
        
        scene_manager = MockSceneManager()
        renderer = MockRenderer()
        audio_manager = MockAudioManager()
        
        game = GameScene(scene_manager, renderer, audio_manager, ai_enabled=True)
        
        # Check that _update_ai_paddle method exists
        assert hasattr(game, '_update_ai_paddle'), "Expected GameScene to have _update_ai_paddle method"
        assert callable(game._update_ai_paddle), "Expected _update_ai_paddle to be callable"
        
        print("✓ AI paddle method exists test passed")
        return True
    except Exception as e:
        print(f"✗ AI paddle method test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    print("Testing AI Opponent Implementation\n")
    
    results = []
    results.append(test_menu_options())
    results.append(test_game_scene_ai_parameter())
    results.append(test_ai_paddle_method_exists())
    
    print("\n" + "=" * 50)
    if all(results):
        print("✓ All AI opponent tests PASSED!")
        sys.exit(0)
    else:
        print("✗ Some AI opponent tests FAILED!")
        sys.exit(1)
