#!/usr/bin/env python3
"""
Quick compilation test - just initializes the game and checks if shaders compile
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_shader_compilation():
    """Test that all style effect shaders compile without errors"""
    import pygame
    import moderngl
    from src.managers.shader_manager import ShaderManager
    from src.utils.constants import WINDOW_WIDTH, WINDOW_HEIGHT
    
    print("Initializing test environment...")
    
    # Initialize Pygame
    pygame.init()
    
    # Create OpenGL window
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN
    )
    
    # Create ModernGL context
    ctx = moderngl.create_context()
    
    # Initialize shader manager
    shader_manager = ShaderManager(ctx)
    
    print("\nTesting shader compilation:")
    print("-" * 40)
    
    # Test scanlines
    scanlines_program = shader_manager.load_shader('style_scanlines', 'basic.vert', 'scanlines.frag')
    if scanlines_program:
        print("✓ Scanlines shader compiled successfully")
    else:
        print("✗ Scanlines shader failed to compile")
        return False
    
    # Test CRT
    crt_program = shader_manager.load_shader('style_crt', 'basic.vert', 'crt.frag')
    if crt_program:
        print("✓ CRT shader compiled successfully")
    else:
        print("✗ CRT shader failed to compile")
        return False
    
    # Test VHS
    vhs_program = shader_manager.load_shader('style_vhs', 'basic.vert', 'vhs.frag')
    if vhs_program:
        print("✓ VHS shader compiled successfully")
    else:
        print("✗ VHS shader failed to compile")
        return False
    
    print("-" * 40)
    
    pygame.quit()
    return True

if __name__ == "__main__":
    try:
        success = test_shader_compilation()
        if success:
            print("\n✓ All shaders compiled successfully!")
            sys.exit(0)
        else:
            print("\n✗ Some shaders failed to compile")
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
