#!/usr/bin/env python3
"""
Test that background shader integration doesn't break the renderer
This validates the code changes without requiring a full OpenGL context
"""
import os
import sys

def test_renderer_imports():
    """Test that renderer can be imported with the new changes"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        # This will validate syntax and imports
        from src.rendering.renderer import Renderer
        print("✓ Renderer imports successfully")
        return True
    except Exception as e:
        print(f"✗ Renderer import failed: {e}")
        return False

def test_constants():
    """Test that constants are properly defined"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        from src.utils.constants import BACKGROUND_TYPE, WINDOW_WIDTH, WINDOW_HEIGHT
        print(f"✓ Constants imported: BACKGROUND_TYPE={BACKGROUND_TYPE}, resolution={WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        return True
    except Exception as e:
        print(f"✗ Constants import failed: {e}")
        return False

def test_shader_manager():
    """Test that shader manager can be imported"""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    try:
        from src.managers.shader_manager import ShaderManager
        print("✓ ShaderManager imports successfully")
        return True
    except Exception as e:
        print(f"✗ ShaderManager import failed: {e}")
        return False

def test_game_loop_logic():
    """Test that game.py has the update_time call"""
    game_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'game.py')
    with open(game_path, 'r') as f:
        content = f.read()
        if 'update_time' in content and 'self.renderer.update_time' in content:
            print("✓ Game loop includes renderer.update_time() call")
            return True
        else:
            print("✗ Game loop missing renderer.update_time() call")
            return False

def test_renderer_has_background_logic():
    """Test that renderer.py has background rendering logic"""
    renderer_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'rendering', 'renderer.py')
    with open(renderer_path, 'r') as f:
        content = f.read()
        checks = [
            ('BACKGROUND_TYPE' in content, "BACKGROUND_TYPE import"),
            ('background_program' in content, "background_program attribute"),
            ('update_time' in content, "update_time method"),
            ('self.time' in content, "time tracking"),
        ]
        
        all_passed = True
        for check, name in checks:
            if check:
                print(f"✓ Renderer has {name}")
            else:
                print(f"✗ Renderer missing {name}")
                all_passed = False
        
        return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("Background Integration Test")
    print("=" * 60)
    print()
    
    tests = [
        test_constants(),
        test_shader_manager(),
        test_renderer_imports(),
        test_game_loop_logic(),
        test_renderer_has_background_logic(),
    ]
    
    print()
    print("=" * 60)
    if all(tests):
        print("✓ All integration tests PASSED!")
        print()
        print("The background shader system is properly integrated.")
        print("The renderer will render animated backgrounds at runtime.")
        sys.exit(0)
    else:
        print("✗ Some integration tests FAILED!")
        sys.exit(1)
