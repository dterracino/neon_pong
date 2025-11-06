#!/usr/bin/env python3
"""
Visual test for the retrowave background shader
Shows the shader in action for visual confirmation
"""
import os
import sys
import pygame
import moderngl

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.managers.shader_manager import ShaderManager
import numpy as np

def test_retrowave_visual():
    """Create a window showing the retrowave shader"""
    
    # Initialize pygame
    pygame.init()
    
    # Create window
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.OPENGL | pygame.DOUBLEBUF
    )
    pygame.display.set_caption("Retrowave Shader Test")
    
    # Create ModernGL context
    ctx = moderngl.create_context()
    ctx.enable(moderngl.BLEND)
    ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA
    
    # Create shader manager and load shader
    shader_manager = ShaderManager(ctx)
    shader_program = shader_manager.load_shader(
        'background_retrowave', 'basic.vert', 'background_retrowave.frag'
    )
    
    if not shader_program:
        print("✗ Failed to load retrowave shader!")
        return False
    
    print("✓ Retrowave shader loaded successfully")
    
    # Create fullscreen quad
    vertices = np.array([
        -1.0, -1.0,
         1.0, -1.0,
        -1.0,  1.0,
         1.0,  1.0,
    ], dtype='f4')
    
    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(shader_program, vbo, 'in_position')
    
    # Main loop
    clock = pygame.time.Clock()
    time = 0.0
    running = True
    
    print("\n" + "=" * 60)
    print("Retrowave Shader Visual Test")
    print("=" * 60)
    print("The window will show the retrowave background shader.")
    print("Features:")
    print("  - Perspective grid floor moving towards you")
    print("  - Gradient purple/pink sky")
    print("  - Animated neon pink sun on the horizon")
    print("  - Scan lines for CRT effect")
    print("  - Cyan grid lines with proper perspective")
    print("\nPress ESC or close window to exit")
    print("=" * 60)
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Update time
        dt = clock.tick(60) / 1000.0
        time += dt
        
        # Clear screen
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        
        # Set uniforms and render
        shader_program['time'] = time
        shader_program['resolution'] = (WINDOW_WIDTH, WINDOW_HEIGHT)
        vao.render(moderngl.TRIANGLE_STRIP)
        
        # Swap buffers
        pygame.display.flip()
    
    pygame.quit()
    print("\n✓ Visual test completed")
    return True

if __name__ == "__main__":
    try:
        success = test_retrowave_visual()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Error during visual test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
