"""
Quick sprite integration test - verify sprites load and render without launching full game
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
import moderngl

def test_sprite_integration():
    """Test sprite loading and integration with renderer"""
    print("Initializing pygame...")
    pygame.init()
    
    # Create minimal OpenGL context
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    pygame.display.gl_set_attribute(
        pygame.GL_CONTEXT_PROFILE_MASK,
        pygame.GL_CONTEXT_PROFILE_CORE
    )
    
    screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF | pygame.HIDDEN)
    ctx = moderngl.create_context()
    
    print("\nTesting AssetManager sprite loading...")
    from src.managers.asset_manager import AssetManager
    asset_manager = AssetManager()
    
    count = asset_manager.preload_images()
    print(f"  ✓ Loaded {count} images")
    
    # Check specific sprites
    paddle1 = asset_manager.get_image('paddle1')
    paddle2 = asset_manager.get_image('paddle2')
    ball = asset_manager.get_image('ball')
    
    print("\nSprite availability:")
    print(f"  paddle1.png: {'✓ Found' if paddle1 else '✗ Not found'}")
    print(f"  paddle2.png: {'✓ Found' if paddle2 else '✗ Not found'}")
    print(f"  ball.png: {'✓ Found' if ball else '✗ Not found'}")
    
    if paddle1:
        print(f"\n  Paddle1 dimensions: {paddle1.get_width()}x{paddle1.get_height()}")
    if paddle2:
        print(f"  Paddle2 dimensions: {paddle2.get_width()}x{paddle2.get_height()}")
    if ball:
        print(f"  Ball dimensions: {ball.get_width()}x{ball.get_height()}")
    
    print("\nTesting Renderer sprite drawing...")
    from src.managers.shader_manager import ShaderManager
    from src.rendering.renderer import Renderer
    
    shader_manager = ShaderManager(ctx)
    renderer = Renderer(ctx, shader_manager)
    
    print("  ✓ Renderer initialized")
    
    # Test draw_sprite method exists
    if hasattr(renderer, 'draw_sprite'):
        print("  ✓ draw_sprite method exists")
    else:
        print("  ✗ draw_sprite method missing!")
        return False
    
    # Test entity sprite support
    print("\nTesting entity sprite support...")
    from src.entities.paddle import Paddle
    from src.entities.ball import Ball
    
    test_paddle = Paddle(100, 100, 1)
    test_ball = Ball(400, 300)
    
    # Check sprite attribute exists
    if hasattr(test_paddle, 'sprite'):
        print("  ✓ Paddle has sprite attribute")
    else:
        print("  ✗ Paddle missing sprite attribute!")
        return False
    
    if hasattr(test_ball, 'sprite'):
        print("  ✓ Ball has sprite attribute")
    else:
        print("  ✗ Ball missing sprite attribute!")
        return False
    
    # Test set_sprite method
    if hasattr(test_paddle, 'set_sprite'):
        print("  ✓ Paddle has set_sprite method")
        test_paddle.set_sprite(paddle1)
        print(f"    Sprite set: {test_paddle.sprite is not None}")
    else:
        print("  ✗ Paddle missing set_sprite method!")
        return False
    
    if hasattr(test_ball, 'set_sprite'):
        print("  ✓ Ball has set_sprite method")
        test_ball.set_sprite(ball)
        print(f"    Sprite set: {test_ball.sprite is not None}")
    else:
        print("  ✗ Ball missing set_sprite method!")
        return False
    
    print("\n" + "="*60)
    print("✓ All sprite integration tests passed!")
    print("="*60)
    
    pygame.quit()
    return True

if __name__ == '__main__':
    try:
        success = test_sprite_integration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
